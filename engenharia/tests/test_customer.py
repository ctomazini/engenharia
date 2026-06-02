import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import (
	_gerar_cnpj_valido,
	_gerar_cpf_valido,
	create_test_customer,
)

VALID_CELULAR = "11987654321"
VALID_EMAIL = "teste@example.com"


class TestCustomer(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_create_individual(self):
		cpf = _gerar_cpf_valido()
		customer = create_test_customer(
			person_type="Pessoa Física",
			customer_name=f"Maria Teste {frappe.generate_hash(length=6)}",
			cpf=cpf,
		)
		self.assertEqual(customer.person_type, "Pessoa Física")
		self.assertEqual(customer.cpf, cpf)
		self.assertTrue(frappe.db.exists("Customer", customer.name))

	def test_create_company(self):
		customer = create_test_customer(
			person_type="Pessoa Jurídica",
			customer_name=f"Empresa Teste {frappe.generate_hash(length=6)}",
			cnpj=_gerar_cnpj_valido(),
		)
		self.assertEqual(customer.person_type, "Pessoa Jurídica")
		self.assertTrue(frappe.db.exists("Customer", customer.name))

	def test_validate_phone_and_email(self):
		customer = create_test_customer(
			phone=VALID_CELULAR,
			email=VALID_EMAIL,
		)
		self.assertEqual(customer.phone, VALID_CELULAR)
		self.assertEqual(customer.email, VALID_EMAIL)

	def test_duplicate_cpf_rejected(self):
		cpf = _gerar_cpf_valido()
		create_test_customer(cpf=cpf)
		with self.assertRaises(frappe.ValidationError):
			create_test_customer(cpf=cpf)

	def test_update_customer(self):
		customer = create_test_customer()
		customer.customer_name = f"Updated {frappe.generate_hash(length=6)}"
		customer.save(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Customer", customer.name))

	def test_delete_customer(self):
		customer = create_test_customer()
		name = customer.name
		customer.delete(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Customer", name))
