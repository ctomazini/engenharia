import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

from engenharia.dashboard_api import mark_payment_received
from engenharia.tests.test_setup import create_test_engineering_contract, get_contract_payments


class TestDashboardApi(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_mark_payment_received_updates_status(self):
		contract = create_test_engineering_contract(base_value=500, installment_count=1)
		payment_name = get_contract_payments(contract.name)[0].name

		result = mark_payment_received(payment_name, today())
		self.assertEqual(result["status"], "Recebido")
		self.assertEqual(frappe.db.get_value("Payment", payment_name, "status"), "Recebido")

	def test_mark_payment_received_requires_write_permission(self):
		contract = create_test_engineering_contract(base_value=500, installment_count=1)
		payment_name = get_contract_payments(contract.name)[0].name

		user = "test_eng_dash_api@example.com"
		if not frappe.db.exists("User", user):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user,
					"first_name": "Test",
					"send_welcome_email": 0,
					"roles": [{"role": "Engenharia User"}],
				}
			).insert(ignore_permissions=True)

		frappe.set_user(user)
		try:
			with self.assertRaises(frappe.PermissionError):
				mark_payment_received(payment_name, today())
		finally:
			frappe.set_user("Administrator")
