import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.engenharia.report.projects_by_status.projects_by_status import execute as projects_by_status
from engenharia.engenharia.report.work_cost_by_project.work_cost_by_project import execute as work_cost_by_project
from engenharia.tests.test_setup import create_test_construction_project, create_test_work_cost


class TestReports(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_projects_by_status_returns_rows(self):
		create_test_construction_project(status="Em andamento")
		columns, data = projects_by_status()
		self.assertTrue(columns)
		self.assertTrue(data)

	def test_work_cost_by_project_with_seed(self):
		project = create_test_construction_project()
		create_test_work_cost(project=project.name, amount=1500)
		columns, data = work_cost_by_project()
		self.assertTrue(any(row.get("project") == project.name for row in data))
