import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.engenharia.report.work_cost_by_category.work_cost_by_category import execute
from engenharia.tests.test_setup import create_test_cost_category, create_test_work_cost


class TestReportWorkCostByCategory(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_execute_groups_by_category(self):
		category = create_test_cost_category().name
		create_test_work_cost(amount=1200, cost_category=category, status="Pago")
		columns, data, _msg, chart, summary = execute()
		self.assertTrue(columns)
		self.assertTrue(any(row.get("cost_category") == category for row in data))
		self.assertIsNotNone(chart)
		self.assertTrue(summary)
