import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

from engenharia.financial import (
	bulk_delete_payments,
	cancel_contract_payment,
	reimbursable_origin_id,
	resync_contract_payments,
	sync_payments_from_contract,
)
from engenharia.tests.test_setup import (
	create_test_engineering_contract,
	create_test_reimbursable_expense,
	get_contract_payments,
)


class TestFinancial(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_sync_creates_payments(self):
		contract = create_test_engineering_contract(base_value=3000, installment_count=3)
		result = sync_payments_from_contract(contract.name)
		self.assertGreaterEqual(
			result.get("created", 0) + len(get_contract_payments(contract.name)), 3
		)

	def test_resync_updates_installment_amount(self):
		contract = create_test_engineering_contract(base_value=1000, installment_count=1)
		payment_name = get_contract_payments(contract.name)[0].name
		contract_doc = frappe.get_doc("Engineering Contract", contract.name)
		contract_doc.installments[0].amount = 1500
		contract_doc.base_value = 1500
		contract_doc.save(ignore_permissions=True)
		resync_contract_payments(contract.name)
		self.assertEqual(flt(frappe.db.get_value("Payment", payment_name, "amount")), 1500)

	def test_contract_without_installments_has_no_payments(self):
		contract = create_test_engineering_contract(
			base_value=0, installment_count=0, installments=[], current_value=0
		)
		contract.installment_count = 0
		contract.save(ignore_permissions=True)
		self.assertEqual(len(get_contract_payments(contract.name)), 0)

	def test_bulk_delete_pending_payments(self):
		contract = create_test_engineering_contract(base_value=2000, installment_count=2)
		names = [p.name for p in get_contract_payments(contract.name)]
		result = bulk_delete_payments(names)
		self.assertEqual(len(result["deleted"]), 2)

	def test_bulk_delete_skips_received(self):
		contract = create_test_engineering_contract(base_value=500, installment_count=1)
		payment = frappe.get_doc("Payment", get_contract_payments(contract.name)[0].name)
		payment.status = "Recebido"
		payment.received_date = today()
		payment.received_amount = payment.amount
		payment.save(ignore_permissions=True)
		result = bulk_delete_payments([payment.name])
		self.assertEqual(len(result["skipped"]), 1)

	def test_payment_received_updates_installment(self):
		contract = create_test_engineering_contract(base_value=800, installment_count=1)
		payment = frappe.get_doc("Payment", get_contract_payments(contract.name)[0].name)
		payment.status = "Recebido"
		payment.received_date = today()
		payment.received_amount = payment.amount
		payment.save(ignore_permissions=True)

		installment = contract.installments[0]
		status = frappe.db.get_value(
			"Engineering Contract Installment", installment.name, "status"
		)
		self.assertEqual(status, "Recebido")

	def test_cancel_contract_payment(self):
		contract = create_test_engineering_contract(base_value=500, installment_count=1)
		payment_name = get_contract_payments(contract.name)[0].name
		cancel_contract_payment(payment_name)
		self.assertEqual(frappe.db.get_value("Payment", payment_name, "status"), "Cancelado")

	def test_reimbursable_payment_included_in_receivable_kpi(self):
		from engenharia.dashboard import kpis as dashboard_kpis

		expense = create_test_reimbursable_expense(amount=250)
		payment_name = frappe.db.get_value(
			"Payment",
			{"installment_origin_id": reimbursable_origin_id(expense.name)},
			"name",
		)
		self.assertTrue(payment_name)

		hoje = today()
		period_end = frappe.utils.add_days(hoje, 7)
		month_start = frappe.utils.get_first_day(hoje)
		month_end = frappe.utils.get_last_day(hoje)
		k = dashboard_kpis.build_kpis(hoje, period_end, month_start, month_end)
		self.assertGreaterEqual(flt(k["amount_receivable"]["amount"]), 250)

	def test_check_overdue_installments_marks_vencido(self):
		from engenharia.tasks import check_overdue_installments

		contract = create_test_engineering_contract(base_value=500, installment_count=1)
		payment = frappe.get_doc("Payment", get_contract_payments(contract.name)[0].name)
		payment.due_date = frappe.utils.add_days(today(), -5)
		payment.status = "Pendente"
		payment.save(ignore_permissions=True)

		check_overdue_installments()
		self.assertEqual(frappe.db.get_value("Payment", payment.name, "status"), "Vencido")
