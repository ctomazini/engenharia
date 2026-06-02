import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.dashboard import get as get_dashboard_data
from engenharia.dashboard_api import get_dashboard_data as api_get_dashboard_data
from engenharia.tests.test_setup import (
	create_test_construction_project,
	create_test_engineering_contract,
	create_test_work_cost,
	get_contract_payments,
)


class TestDashboard(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_get_dashboard_data(self):
		project = create_test_construction_project(status="Em andamento")
		contract = create_test_engineering_contract(project=project.name)
		self.assertTrue(get_contract_payments(contract.name))
		create_test_work_cost(project=project.name, amount=500)

		payload = get_dashboard_data()
		self.assertIn("kpis", payload)
		self.assertIn("financeiro", payload)
		self.assertIn("timeline", payload)
		self.assertGreaterEqual(payload["kpis"]["active_projects"], 1)
		self.assertGreaterEqual(payload["kpis"]["month_costs"]["count"], 1)

	def test_api_facade(self):
		payload = api_get_dashboard_data()
		self.assertIn("resumo", payload)

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
