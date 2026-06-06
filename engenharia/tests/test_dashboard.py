import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.dashboard import get as get_dashboard_data
from engenharia.dashboard import agenda as dashboard_agenda
from engenharia.dashboard import attention as dashboard_attention
from engenharia.dashboard import deadlines as dashboard_deadlines
from engenharia.dashboard import financial as dashboard_financial
from engenharia.dashboard import health as dashboard_health
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
	"atencao",
	"saude_operacional",
	"agenda_days",
	"agenda_summary",
	"agenda",
	"timeline",
	"parcelas",
	"despesas_pendentes",
	"total_despesas_mes",
	"horas_periodo",
	"horas_semana",
)

TILE_KEYS = ("count", "tone", "icon", "deep_link", "label")


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
		self.assertTrue(payload.get("is_manager"))

		self.assertEqual(payload["period_days"], payload["periodo_dias"])
		self.assertIn("grafico", payload["financeiro"])
		self.assertIn("fluxo", payload["financeiro"])
		self.assertIn("taxa_recebimento", payload["financeiro"])
		self.assertIsInstance(payload["financeiro"]["grafico"], list)
		self.assertLessEqual(len(payload["financeiro"]["grafico"]), 2)
		for row in payload["financeiro"]["grafico"]:
			self.assertIn("valor", row)
			self.assertNotIn("<div", str(row.get("valor", "")))
		self.assertIn("entrada", payload["financeiro"]["fluxo"])
		self.assertIn("saida", payload["financeiro"]["fluxo"])

	def test_attention_tiles_shape(self):
		hoje = frappe.utils.today()
		period_end = frappe.utils.add_days(hoje, 7)
		month_start = frappe.utils.get_first_day(hoje)
		month_end = frappe.utils.get_last_day(hoje)
		k = dashboard_kpis.build_kpis(hoje, period_end, month_start, month_end)
		fin = dashboard_financial.build_financial(hoje, period_end, k)
		atencao = dashboard_attention.build_attention_tiles(hoje, period_end, 7, k, fin)

		self.assertIn("tiles", atencao)
		self.assertIn("all_clear", atencao)
		for tile in atencao["tiles"]:
			for key in TILE_KEYS:
				self.assertIn(key, tile, msg=f"missing tile key {key}")
			self.assertGreater(tile["count"], 0)
			self.assertIn("doctype", tile["deep_link"])
			self.assertIn("filters", tile["deep_link"])

	def test_operational_health_shape(self):
		hoje = frappe.utils.today()
		period_end = frappe.utils.add_days(hoje, 7)
		month_start = frappe.utils.get_first_day(hoje)
		month_end = frappe.utils.get_last_day(hoje)
		k = dashboard_kpis.build_kpis(hoje, period_end, month_start, month_end)
		fin = dashboard_financial.build_financial(hoje, period_end, k)
		centro = dashboard_deadlines.build_centro_atencao(hoje, period_end, k, fin)
		health = dashboard_health.build_operational_health(k, centro, fin)

		self.assertIn("score", health)
		self.assertIn("tone", health)
		self.assertIn("label", health)
		self.assertIn("breakdown", health)
		self.assertGreaterEqual(health["score"], 0)
		self.assertLessEqual(health["score"], 100)

	def test_agenda_modules(self):
		hoje = frappe.utils.today()
		period_end = frappe.utils.add_days(hoje, 7)
		deadlines = dashboard_deadlines.get_deadlines(hoje, period_end, 20)
		tasks = []
		payments = []
		agenda = dashboard_agenda.build_agenda(hoje, period_end, deadlines, tasks, payments)
		strip = dashboard_agenda.build_day_strip(hoje, 7, agenda)

		self.assertIsInstance(agenda, list)
		self.assertLessEqual(len(strip), 7)
		for day in strip:
			self.assertIn("label", day)
			self.assertIn("count", day)
			self.assertIn("tone", day)

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
		self.assertIn("atencao", payload)
		self.assertIn("saude_operacional", payload)

	def test_list_limits_respected(self):
		payload = get_dashboard_data(list_limits={"parcelas": 10, "timeline": 5})
		self.assertLessEqual(len(payload["parcelas"]), 10)
		self.assertLessEqual(len(payload["agenda"]), 5)
		self.assertEqual(payload["list_limits"]["parcelas"], 10)
		self.assertEqual(payload["list_meta"]["parcelas"]["showing"], len(payload["parcelas"]))

	def test_list_limits_normalize_invalid(self):
		payload = get_dashboard_data(list_limits={"parcelas": 3, "timeline": 2})
		self.assertEqual(payload["list_limits"]["parcelas"], 5)
		self.assertEqual(payload["list_limits"]["timeline"], 5)

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
