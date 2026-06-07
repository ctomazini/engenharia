import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.engenharia.report.work_cost_by_project.work_cost_by_project import execute
from engenharia.tests.test_setup import create_test_construction_project, create_test_work_cost


class TestReportWorkCostByProject(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_execute_includes_project_row(self):
		project = create_test_construction_project()
		create_test_work_cost(project=project.name, amount=1500)
		columns, data, _msg, chart, summary = execute()
		self.assertTrue(any(row.get("project") == project.name for row in data))
		self.assertIsNotNone(chart)
		self.assertTrue(summary)
