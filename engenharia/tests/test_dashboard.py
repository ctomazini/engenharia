import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.dashboard import get as get_dashboard_data
from engenharia.dashboard import deadlines as dashboard_deadlines
from engenharia.dashboard import financial as dashboard_financial
from engenharia.dashboard import kpis as dashboard_kpis
from engenharia.dashboard_api import get_dashboard_data as api_get_dashboard_data
from engenharia.tests.test_setup import (
	create_test_construction_project,
	create_test_engineering_contract,
	create_test_work_cost,
	get_contract_payments,
)

CONTRACT_KEYS = (
	"period_days",
	"periodo_dias",
	"list_limits",
	"list_meta",
	"kpis",
	"resumo",
	"financeiro",
	"centro_atencao",
	"timeline",
	"parcelas",
	"despesas_pendentes",
	"total_despesas_mes",
	"horas_periodo",
	"horas_semana",
)


class TestDashboard(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_get_dashboard_data_contract(self):
		project = create_test_construction_project(status="Em andamento")
		contract = create_test_engineering_contract(project=project.name)
		self.assertTrue(get_contract_payments(contract.name))
		create_test_work_cost(project=project.name, amount=500)

		payload = get_dashboard_data()
		for key in CONTRACT_KEYS:
			self.assertIn(key, payload, msg=f"missing key {key}")

		self.assertEqual(payload["period_days"], payload["periodo_dias"])
		self.assertIn("grafico", payload["financeiro"])
		self.assertIn("taxa_recebimento", payload["financeiro"])
		self.assertIsInstance(payload["financeiro"]["grafico"], list)
		for row in payload["financeiro"]["grafico"]:
			self.assertIn("valor", row)
			self.assertNotIn("<div", str(row.get("valor", "")))

	def test_kpis_amounts_are_numeric(self):
		payload = get_dashboard_data()
		receivable = payload["kpis"]["amount_receivable"]["amount"]
		self.assertIsInstance(receivable, (int, float))

	def test_centro_atencao_shape(self):
		hoje = frappe.utils.today()
		period_end = frappe.utils.add_days(hoje, 7)
		month_start = frappe.utils.get_first_day(hoje)
		month_end = frappe.utils.get_last_day(hoje)
		k = dashboard_kpis.build_kpis(hoje, period_end, month_start, month_end)
		fin = dashboard_financial.build_financial(hoje, period_end, k)
		centro = dashboard_deadlines.build_centro_atencao(hoje, period_end, k, fin)
		self.assertIn("parcelas_vencidas", centro)
		self.assertIn("pagamentos_periodo", centro)

	def test_api_facade(self):
		payload = api_get_dashboard_data()
		self.assertIn("resumo", payload)
		self.assertIn("centro_atencao", payload)

	def test_permission_required(self):
		user_email = f"dash_no_perm_{frappe.generate_hash(length=6)}@example.com"
		if not frappe.db.exists("User", user_email):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user_email,
					"first_name": "Dash",
					"last_name": "NoPerm",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)

		frappe.set_user(user_email)
		try:
			from frappe.exceptions import PermissionError

			with self.assertRaises(PermissionError):
				get_dashboard_data()
		finally:
			frappe.set_user("Administrator")
