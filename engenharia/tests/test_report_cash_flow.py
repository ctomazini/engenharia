import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

from engenharia.engenharia.report.cash_flow.cash_flow import execute
from engenharia.tests.test_setup import create_test_reimbursable_expense


class TestReportCashFlow(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_execute_returns_outflow_for_reimbursable(self):
		expense = create_test_reimbursable_expense(amount=350)
		expense.payment_date = today()
		expense.save(ignore_permissions=True)

		columns, data, _msg, chart, summary = execute({"months": 1})
		self.assertTrue(columns)
		self.assertIsInstance(data, list)
		self.assertIsNotNone(chart)
		self.assertEqual(len(summary), 3)

	def test_execute_without_filters(self):
		columns, data, _msg, _chart, _summary = execute({})
		self.assertTrue(columns)
		self.assertIsInstance(data, list)
