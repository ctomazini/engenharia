import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

from engenharia.engenharia.report.project_margin.project_margin import execute
from engenharia.tests.test_setup import (
	create_test_construction_project,
	create_test_engineering_contract,
	create_test_work_cost,
	get_contract_payments,
)


class TestReportProjectMargin(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_execute_includes_realized_margin(self):
		project = create_test_construction_project()
		contract = create_test_engineering_contract(project=project.name, base_value=10000, installment_count=1)
		create_test_work_cost(project=project.name, amount=2000, status="Pago")

		payment = frappe.get_doc("Payment", get_contract_payments(contract.name)[0].name)
		payment.status = "Recebido"
		payment.received_date = today()
		payment.received_amount = payment.amount
		payment.save(ignore_permissions=True)

		columns, data, _msg, chart, summary = execute({})
		row = next(r for r in data if r["project"] == project.name)
		fieldnames = {c["fieldname"] for c in columns}
		self.assertIn("realized_margin", fieldnames)
		self.assertGreater(flt(row["received_revenue"]), 0)
		self.assertIsNotNone(chart)
		self.assertTrue(summary)
