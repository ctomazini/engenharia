import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.dashboard_api import get_dashboard_data, mark_payment_received
from engenharia.documents import get_placeholder_reference
from engenharia.financial import bulk_delete_payments, cancel_contract_payment, resync_contract_payments
from engenharia.tests.test_setup import create_test_engineering_contract, get_contract_payments


class TestWhitelist(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_get_dashboard_data_requires_project_read(self):
		user = "test_whitelist_dash@example.com"
		if not frappe.db.exists("User", user):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user,
					"first_name": "Test",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)

		frappe.set_user(user)
		try:
			with self.assertRaises(frappe.PermissionError):
				get_dashboard_data()
		finally:
			frappe.set_user("Administrator")

	def test_get_placeholder_reference_requires_read(self):
		result = get_placeholder_reference()
		self.assertTrue(result)

	def test_resync_contract_payments_whitelist(self):
		contract = create_test_engineering_contract(base_value=1000, installment_count=1)
		result = resync_contract_payments(contract.name)
		self.assertEqual(result["status"], "ok")

	def test_bulk_delete_payments_whitelist(self):
		contract = create_test_engineering_contract(base_value=1000, installment_count=1)
		names = [p.name for p in get_contract_payments(contract.name)]
		result = bulk_delete_payments(names)
		self.assertEqual(len(result["deleted"]), 1)

	def test_cancel_contract_payment_whitelist(self):
		contract = create_test_engineering_contract(base_value=1000, installment_count=1)
		payment_name = get_contract_payments(contract.name)[0].name
		result = cancel_contract_payment(payment_name)
		self.assertTrue(result["success"])
		self.assertEqual(frappe.db.get_value("Payment", payment_name, "status"), "Cancelado")

	def test_mark_payment_received_facade_has_permission(self):
		import inspect

		source = inspect.getsource(mark_payment_received)
		self.assertIn("has_permission", source)
		self.assertIn("Payment", source)
