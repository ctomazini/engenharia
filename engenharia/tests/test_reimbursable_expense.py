import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

from engenharia.financial import ORIGIN_REIMBURSABLE, reimbursable_origin_id
from engenharia.tests.test_setup import create_test_construction_project, create_test_reimbursable_expense


class TestReimbursableExpense(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_crud(self):
		expense = create_test_reimbursable_expense(amount=750)
		self.assertTrue(frappe.db.exists("Reimbursable Expense", expense.name))
		self.assertTrue(expense.customer)
		name = expense.name
		expense.delete(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Reimbursable Expense", name))

	def test_customer_from_project(self):
		project = create_test_construction_project()
		expense = create_test_reimbursable_expense(project=project.name)
		self.assertEqual(expense.customer, project.customer)

	def test_reimbursement_status(self):
		expense = create_test_reimbursable_expense()
		expense.client_reimbursed_date = today()
		expense.save(ignore_permissions=True)
		expense.reload()
		self.assertEqual(expense.status, "Reembolsado")

	def test_cancelled_immutable(self):
		expense = create_test_reimbursable_expense(status="Cancelado")
		expense.amount = 999
		with self.assertRaises(ValidationError):
			expense.save(ignore_permissions=True)

	def test_sync_creates_payment(self):
		expense = create_test_reimbursable_expense(amount=300)
		payment = frappe.db.get_value(
			"Payment",
			{"installment_origin_id": reimbursable_origin_id(expense.name)},
			["name", "status", "amount", "origin_type"],
			as_dict=True,
		)
		self.assertTrue(payment)
		self.assertEqual(payment.origin_type, ORIGIN_REIMBURSABLE)
		self.assertEqual(payment.status, "Pendente")
		self.assertEqual(flt(payment.amount), 300)
		expense.reload()
		self.assertEqual(expense.payment, payment.name)

	def test_payment_received_updates_expense(self):
		expense = create_test_reimbursable_expense(amount=420)
		payment_name = frappe.db.get_value(
			"Payment",
			{"installment_origin_id": reimbursable_origin_id(expense.name)},
			"name",
		)
		payment = frappe.get_doc("Payment", payment_name)
		payment.status = "Recebido"
		payment.received_date = today()
		payment.received_amount = payment.amount
		payment.save(ignore_permissions=True)

		expense.reload()
		self.assertEqual(expense.status, "Reembolsado")
		self.assertEqual(str(expense.client_reimbursed_date), today())

	def test_cancel_expense_cancels_payment(self):
		expense = create_test_reimbursable_expense()
		payment_name = frappe.db.get_value(
			"Payment",
			{"installment_origin_id": reimbursable_origin_id(expense.name)},
			"name",
		)
		expense.status = "Cancelado"
		expense.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Payment", payment_name, "status"), "Cancelado")

	def test_no_payment_when_client_reimbursement_disabled(self):
		expense = create_test_reimbursable_expense(await_client_reimbursement=0)
		payment_name = frappe.db.get_value(
			"Payment",
			{"installment_origin_id": reimbursable_origin_id(expense.name)},
			"name",
		)
		self.assertFalse(payment_name)
