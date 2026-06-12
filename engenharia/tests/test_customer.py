import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import (
	_gerar_cnpj_valido,
	_gerar_cpf_valido,
	create_test_customer,
)

VALID_CELULAR = "11987654321"
VALID_FIXO = "1132345678"
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

	def test_contacts_and_addresses(self):
		customer = create_test_customer(
			contacts=[
				{
					"contact_name": "Contato",
					"contact_type": "Principal",
					"phone": VALID_FIXO,
					"mobile": VALID_CELULAR,
					"email": VALID_EMAIL,
					"notes": "Preferir contato por e-mail",
				}
			],
			addresses=[
				{
					"address_type": "Residencial",
					"street": "Rua Teste",
					"number": "123",
					"complement": "Apto 4",
					"district": "Centro",
					"cep": "01310100",
					"city": "São Paulo",
					"state": "SP",
					"is_primary": 1,
				}
			],
		)
		self.assertEqual(len(customer.contacts), 1)
		contact = customer.contacts[0]
		self.assertEqual(contact.phone, VALID_FIXO)
		self.assertEqual(contact.mobile, VALID_CELULAR)
		self.assertEqual(contact.email, VALID_EMAIL)
		self.assertEqual(contact.notes, "Preferir contato por e-mail")
		self.assertEqual(len(customer.addresses), 1)
		address = customer.addresses[0]
		self.assertEqual(address.street, "Rua Teste")
		self.assertEqual(address.number, "123")
		self.assertEqual(address.complement, "Apto 4")
		self.assertEqual(address.district, "Centro")
		self.assertEqual(address.cep, "01310100")
		self.assertEqual(address.is_primary, 1)

	def test_before_save_clears_opposite_type_fields(self):
		customer = create_test_customer(
			person_type="Pessoa Física",
			legal_representative="Não deve persistir",
			cnpj=_gerar_cnpj_valido(),
		)
		self.assertFalse(customer.cnpj)
		self.assertFalse(customer.legal_representative)

	def test_legal_representative_cpf_validated(self):
		customer = create_test_customer(
			person_type="Pessoa Jurídica",
			legal_representative_cpf=_gerar_cpf_valido(),
		)
		self.assertTrue(customer.legal_representative_cpf)

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

	def test_autoname_prefix(self):
		customer = create_test_customer()
		self.assertTrue(customer.name.startswith("CLI-"))

	def test_birth_date_and_rg_issuer(self):
		"""Verifica que birth_date e rg_issuer salvam para PF e são limpos para PJ."""
		customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"person_type": "Pessoa Física",
				"customer_name": f"_Test PF Birth {frappe.generate_hash(length=6)}",
				"cpf": "52998224725",
				"birth_date": "1990-06-15",
				"rg_issuer": "SSP/RS",
			}
		)
		customer.insert(ignore_permissions=True)
		self.assertEqual(str(customer.birth_date), "1990-06-15")
		self.assertEqual(customer.rg_issuer, "SSP/RS")
