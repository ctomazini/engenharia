import frappe
from frappe.tests.utils import FrappeTestCase


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
