from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from engenharia.notifications import (
	notify_deadlines_daily,
	notify_expiring_permits,
	notify_overdue_payments,
	notify_overdue_tasks,
)
from engenharia.tests.test_setup import (
	create_test_deadline,
	create_test_payment,
	create_test_permit,
	create_test_task,
)


NOTIFICATION_NAMES = (
	"Engenharia - Prazo vencendo",
	"Engenharia - Parcela vencida",
	"Engenharia - Protocolo expirando",
	"Engenharia - Tarefa atrasada",
)


class TestNotifications(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_notification_fixtures_exist(self):
		for name in NOTIFICATION_NAMES:
			self.assertTrue(
				frappe.db.exists("Notification", name),
				msg=f"Notification {name} não encontrada — rode migrate",
			)

	@patch("frappe.sendmail")
	def test_notify_deadlines_daily_sends_email(self, mock_sendmail):
		create_test_deadline(due_date=add_days(today(), 1), notify_days_before=3)
		notify_deadlines_daily()
		if mock_sendmail.called:
			kwargs = mock_sendmail.call_args.kwargs
			self.assertIn("recipients", kwargs)
			self.assertTrue(kwargs["recipients"])
			self.assertIn("Engenharia", kwargs.get("subject", ""))

	@patch("frappe.sendmail")
	@patch("engenharia.notifications.frappe.get_all")
	def test_notify_deadlines_daily_skips_distant_deadlines(self, mock_get_all, mock_sendmail):
		mock_get_all.return_value = [
			frappe._dict(
				name="DLNE-TEST",
				project="PROJ-TEST",
				customer="CUST-TEST",
				due_date=add_days(today(), 30),
				description="Prazo distante",
				priority="Normal",
				assigned_to=None,
				notify_days_before=3,
			)
		]
		notify_deadlines_daily()
		mock_sendmail.assert_not_called()

	@patch("engenharia.notifications.enqueue_create_notification")
	def test_notify_overdue_tasks_creates_alert(self, mock_enqueue):
		create_test_task(due_date=add_days(today(), -2), status="A fazer")
		notify_overdue_tasks()
		self.assertTrue(mock_enqueue.called)

	@patch("engenharia.notifications.enqueue_create_notification")
	def test_notify_overdue_payments_creates_alert(self, mock_enqueue):
		payment = create_test_payment()
		frappe.db.set_value(
			"Payment",
			payment.name,
			{"status": "Vencido", "due_date": add_days(today(), -3)},
			update_modified=False,
		)
		notify_overdue_payments()
		self.assertTrue(mock_enqueue.called)

	@patch("engenharia.notifications.enqueue_create_notification")
	def test_notify_expiring_permits_creates_alert(self, mock_enqueue):
		create_test_permit(expiry_date=add_days(today(), 15), status="Aprovado")
		notify_expiring_permits()
		self.assertTrue(mock_enqueue.called)
