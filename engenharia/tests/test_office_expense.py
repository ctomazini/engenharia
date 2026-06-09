import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, today

from engenharia.engenharia.doctype.office_expense.office_expense import create_next_office_expense
from engenharia.tasks import check_overdue_office_expenses
from engenharia.tests.test_setup import create_test_office_expense


class TestOfficeExpense(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_create_pending(self):
		doc = create_test_office_expense(due_date=add_days(today(), 30))
		self.assertEqual(doc.status, "Pendente")

	def test_past_due_marks_overdue(self):
		doc = create_test_office_expense(due_date=add_days(today(), -3))
		doc.reload()
		self.assertEqual(doc.status, "Atrasado")

	def test_payment_date_marks_paid(self):
		doc = create_test_office_expense()
		doc.payment_date = today()
		doc.save(ignore_permissions=True)
		doc.reload()
		self.assertEqual(doc.status, "Pago")

	def test_recurring_monthly_next_due(self):
		doc = create_test_office_expense(
			due_date="2026-06-01",
			is_recurring=1,
			recurrence_frequency="Mensal",
		)
		self.assertEqual(getdate(doc.next_due_date), getdate("2026-07-01"))

	def test_scheduler_marks_overdue(self):
		doc = create_test_office_expense(due_date=add_days(today(), -2))
		frappe.db.set_value("Office Expense", doc.name, "status", "Pendente")
		check_overdue_office_expenses()
		self.assertEqual(frappe.db.get_value("Office Expense", doc.name, "status"), "Atrasado")

	def test_paid_not_changed_by_scheduler(self):
		doc = create_test_office_expense(due_date=add_days(today(), -2))
		frappe.db.set_value("Office Expense", doc.name, "status", "Pago")
		check_overdue_office_expenses()
		self.assertEqual(frappe.db.get_value("Office Expense", doc.name, "status"), "Pago")

	def test_create_next_recurring(self):
		doc = create_test_office_expense(
			due_date="2026-06-01",
			is_recurring=1,
			recurrence_frequency="Mensal",
		)
		nova_name = create_next_office_expense(doc.name)
		nova = frappe.get_doc("Office Expense", nova_name)
		self.assertEqual(getdate(nova.due_date), getdate("2026-07-01"))
		self.assertEqual(nova.status, "Pendente")

	def test_create_next_not_recurring_fails(self):
		doc = create_test_office_expense(is_recurring=0)
		with self.assertRaises(ValidationError):
			create_next_office_expense(doc.name)

	def test_description_required(self):
		with self.assertRaises(MandatoryError):
			frappe.get_doc(
				{
					"doctype": "Office Expense",
					"expense_category": "Aluguel",
					"amount": 100,
				}
			).insert(ignore_permissions=True)

	def test_composed_title(self):
		doc = create_test_office_expense(description="Aluguel sala")
		self.assertIn(doc.name, doc.title)
		self.assertIn("Aluguel sala", doc.title)
