from frappe.tests.utils import FrappeTestCase

from engenharia.validators import formatar_cep, formatar_cnpj, formatar_cpf, formatar_telefone


class TestFormatters(FrappeTestCase):
	def test_formatar_cpf(self):
		self.assertEqual(formatar_cpf("12345678909"), "123.456.789-09")

	def test_formatar_cnpj(self):
		self.assertEqual(formatar_cnpj("11222333000181"), "11.222.333/0001-81")

	def test_formatar_telefone_celular(self):
		self.assertEqual(formatar_telefone("11987654321"), "(11) 98765-4321")

	def test_formatar_telefone_fixo(self):
		self.assertEqual(formatar_telefone("1132345678"), "(11) 3234-5678")

	def test_formatar_cep(self):
		self.assertEqual(formatar_cep("01001000"), "01001-000")
