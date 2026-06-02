import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

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
		expense.reimbursement_date = today()
		expense.save(ignore_permissions=True)
		expense.reload()
		self.assertEqual(expense.status, "Reembolsado")

	def test_cancelled_immutable(self):
		expense = create_test_reimbursable_expense(status="Cancelado")
		expense.amount = 999
		with self.assertRaises(ValidationError):
			expense.save(ignore_permissions=True)
