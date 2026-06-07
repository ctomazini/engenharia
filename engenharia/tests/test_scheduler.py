from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from engenharia.tasks import (
	check_overdue_installments,
	check_overdue_reimbursable_expenses,
	check_project_status_weekly,
)
from engenharia.tests.test_setup import (
	create_test_construction_project,
	create_test_deadline,
	create_test_engineering_contract,
	create_test_payment,
	create_test_reimbursable_expense,
	get_contract_payments,
)


class TestScheduler(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_check_overdue_installments_marks_vencido(self):
		payment = create_test_payment()
		frappe.db.set_value(
			"Payment",
			payment.name,
			{"due_date": add_days(today(), -1), "status": "Pendente", "manual_override": 0},
			update_modified=False,
		)
		check_overdue_installments()
		self.assertEqual(frappe.db.get_value("Payment", payment.name, "status"), "Vencido")

	@patch("engenharia.notifications._send_system_notification")
	def test_check_overdue_reimbursable_expenses_notifies(self, mock_notify):
		expense = create_test_reimbursable_expense()
		frappe.db.set_value(
			"Reimbursable Expense",
			expense.name,
			{"payment_date": add_days(today(), -90), "status": "A reembolsar"},
			update_modified=False,
		)
		check_overdue_reimbursable_expenses()
		self.assertTrue(mock_notify.called)

	def test_check_project_status_weekly_marks_concluded(self):
		project = create_test_construction_project(status="Em andamento")
		check_project_status_weekly()
		self.assertEqual(
			frappe.db.get_value("Construction Project", project.name, "status"),
			"Concluída",
		)

	def test_check_project_status_weekly_keeps_open_contract(self):
		project = create_test_construction_project(status="Em andamento")
		create_test_engineering_contract(project=project.name)
		check_project_status_weekly()
		self.assertEqual(
			frappe.db.get_value("Construction Project", project.name, "status"),
			"Em andamento",
		)

	def test_check_project_status_weekly_keeps_pending_payment(self):
		project = create_test_construction_project(status="Em andamento")
		contract = create_test_engineering_contract(project=project.name, installment_count=1)
		payment_name = get_contract_payments(contract.name)[0].name
		frappe.db.set_value(
			"Payment",
			payment_name,
			{"status": "Pendente", "due_date": add_days(today(), 5)},
			update_modified=False,
		)
		check_project_status_weekly()
		self.assertEqual(
			frappe.db.get_value("Construction Project", project.name, "status"),
			"Em andamento",
		)

	def test_check_project_status_weekly_keeps_pending_deadline(self):
		project = create_test_construction_project(status="Em andamento")
		create_test_deadline(project=project.name, status="Pendente")
		check_project_status_weekly()
		self.assertEqual(
			frappe.db.get_value("Construction Project", project.name, "status"),
			"Em andamento",
		)
