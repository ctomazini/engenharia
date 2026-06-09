import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

from engenharia.engenharia.report.budget_vs_actual.budget_vs_actual import execute
from engenharia.tests.test_setup import create_test_construction_project, create_test_work_cost
from engenharia.tests.test_subcontract import create_test_subcontract


class TestBudgetVsActualReport(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_execute_compares_budget_and_realized(self):
		project = create_test_construction_project()
		frappe.db.set_value("Construction Project", project.name, "spec_project_total", 10000)

		create_test_work_cost(project=project.name, amount=2000, status="Paid")
		create_test_subcontract(
			project=project.name,
			total_value=3000,
			payments=[{"payment_date": today(), "amount": 1000}],
		)

		columns, data, _message, chart, report_summary = execute({"project": project.name})

		fieldnames = {col["fieldname"] for col in columns}
		self.assertIn("budget_total", fieldnames)
		self.assertIn("realized_committed", fieldnames)
		self.assertIn("budget_variance", fieldnames)

		row = next(item for item in data if item["project"] == project.name)
		self.assertEqual(flt(row["budget_total"]), 10000)
		self.assertEqual(flt(row["realized_committed"]), 5000)
		self.assertEqual(flt(row["realized_paid"]), 3000)
		self.assertEqual(flt(row["budget_variance"]), 5000)
		self.assertTrue(report_summary)
		self.assertTrue(chart)

	def test_skips_projects_without_budget_or_realized(self):
		project = create_test_construction_project()
		_columns, data, _message, chart, _report_summary = execute({"project": project.name})
		self.assertEqual(data, [])
		self.assertIsNone(chart)
