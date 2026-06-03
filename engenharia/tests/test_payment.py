import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import create_test_engineering_contract, get_contract_payments


class TestPayment(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_payment_has_title(self):
		contract = create_test_engineering_contract(base_value=1000, installment_count=1)
		payment_name = get_contract_payments(contract.name)[0].name
		title = frappe.db.get_value("Payment", payment_name, "title")
		self.assertTrue(title)
		self.assertIn(payment_name, title)

	def test_duplicate_origin_id_rejected(self):
		contract = create_test_engineering_contract(base_value=1000, installment_count=1)
		payment = frappe.get_doc("Payment", get_contract_payments(contract.name)[0].name)
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Payment",
					"project": payment.project,
					"customer": payment.customer,
					"contract": payment.contract,
					"origin_type": "Parcela do Contrato",
					"installment_origin_id": payment.installment_origin_id,
					"amount": 100,
					"due_date": payment.due_date,
					"status": "Pendente",
				}
			).insert(ignore_permissions=True)

	def test_cancelled_payment_immutable(self):
		contract = create_test_engineering_contract(base_value=500, installment_count=1)
		payment = frappe.get_doc("Payment", get_contract_payments(contract.name)[0].name)
		payment.status = "Cancelado"
		payment.save(ignore_permissions=True)
		payment.amount = 999
		with self.assertRaises(frappe.ValidationError):
			payment.save(ignore_permissions=True)

	def test_status_visible_in_list_view(self):
		status_field = frappe.get_meta("Payment").get_field("status")
		self.assertEqual(status_field.in_list_view, 1)
