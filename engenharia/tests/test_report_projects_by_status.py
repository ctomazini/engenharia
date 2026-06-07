from engenharia.engenharia.report.projects_by_status.projects_by_status import execute
from engenharia.tests.test_setup import create_test_construction_project
from frappe.tests.utils import FrappeTestCase
import frappe


class TestReportProjectsByStatus(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_execute_returns_chart_and_summary(self):
		create_test_construction_project(status="Em andamento")
		columns, data, _msg, chart, summary = execute()
		self.assertTrue(columns)
		self.assertTrue(data)
		self.assertIsNotNone(chart)
		self.assertTrue(summary)
