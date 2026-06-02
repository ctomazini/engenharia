import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.agent_api import get_active_projects, get_costs_by_category, get_project_summary
from engenharia.tests.test_setup import create_test_construction_project, create_test_cost_category, create_test_work_cost


class TestAgentApi(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_get_active_projects(self):
		create_test_construction_project(status="Em andamento")
		rows = get_active_projects()
		self.assertTrue(rows)
		self.assertIn("customer_name", rows[0])

	def test_get_project_summary(self):
		project = create_test_construction_project(status="Em andamento")
		create_test_work_cost(project=project.name, amount=800)
		summary = get_project_summary(project.name)
		self.assertEqual(summary["project"], project.name)
		self.assertGreaterEqual(summary["total_costs"], 800)

	def test_get_costs_by_category(self):
		project = create_test_construction_project()
		category = create_test_cost_category().name
		create_test_work_cost(project=project.name, amount=300, cost_category=category)
		result = get_costs_by_category(project.name)
		self.assertEqual(result["project"], project.name)
		self.assertGreaterEqual(result["total"], 300)
		self.assertTrue(result["categories"])

	def test_permission_denied_without_access(self):
		user_email = f"agent_no_perm_{frappe.generate_hash(length=6)}@example.com"
		if not frappe.db.exists("User", user_email):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user_email,
					"first_name": "Agent",
					"last_name": "NoPerm",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)

		frappe.set_user(user_email)
		try:
			from frappe.exceptions import PermissionError

			with self.assertRaises(PermissionError):
				get_active_projects()
		finally:
			frappe.set_user("Administrator")
