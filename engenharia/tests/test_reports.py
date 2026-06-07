import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

from engenharia.engenharia.report.cash_flow.cash_flow import execute as cash_flow
from engenharia.engenharia.report.project_margin.project_margin import execute as project_margin
from engenharia.engenharia.report.projects_by_status.projects_by_status import execute as projects_by_status
from engenharia.engenharia.report.work_cost_by_project.work_cost_by_project import execute as work_cost_by_project
from engenharia.tests.test_setup import (
	create_test_construction_project,
	create_test_engineering_contract,
	create_test_reimbursable_expense,
	create_test_work_cost,
	get_contract_payments,
)


class TestReports(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_projects_by_status_returns_rows(self):
		create_test_construction_project(status="Em andamento")
		columns, data, _message, chart, report_summary = projects_by_status()
		self.assertTrue(columns)
		self.assertTrue(data)
		self.assertIsNotNone(chart)
		self.assertTrue(report_summary)

	def test_work_cost_by_project_with_seed(self):
		project = create_test_construction_project()
		create_test_work_cost(project=project.name, amount=1500)
		columns, data, _message, chart, report_summary = work_cost_by_project()
		self.assertTrue(any(row.get("project") == project.name for row in data))
		self.assertIsNotNone(chart)
		self.assertTrue(report_summary)

	def test_project_margin_includes_realized_columns(self):
		project = create_test_construction_project()
		contract = create_test_engineering_contract(project=project.name, base_value=10000, installment_count=1)
		create_test_work_cost(project=project.name, amount=2000, status="Pago")
		create_test_reimbursable_expense(project=project.name, amount=500)

		payment = frappe.get_doc("Payment", get_contract_payments(contract.name)[0].name)
		payment.status = "Recebido"
		payment.received_date = today()
		payment.received_amount = payment.amount
		payment.save(ignore_permissions=True)

		columns, data, _message, chart, report_summary = project_margin()
		row = next(r for r in data if r["project"] == project.name)
		self.assertIsNotNone(chart)
		self.assertTrue(report_summary)
		fieldnames = {c["fieldname"] for c in columns}
		self.assertIn("received_revenue", fieldnames)
		self.assertIn("realized_margin", fieldnames)
		self.assertGreater(flt(row["received_revenue"]), 0)

	def test_cash_flow_includes_reimbursable_outflow(self):
		expense = create_test_reimbursable_expense(amount=350)
		expense.payment_date = today()
		expense.save(ignore_permissions=True)

		columns, data, _message, chart, report_summary = cash_flow({"months": 1})
		self.assertTrue(
			any(flt(row.get("outflow")) >= 350 for row in data if row.get("description"))
		)
		self.assertIsNotNone(chart)
		self.assertEqual(len(report_summary), 3)
