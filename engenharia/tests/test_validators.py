from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase

from engenharia.validators import (
	_calcular_dv_cnpj,
	formatar_cnpj,
	limpar_cnpj,
	validar_cnpj,
)


class TestCnpjAlfanumerico(FrappeTestCase):
	def test_limpar_cnpj_preserva_letras(self):
		self.assertEqual(limpar_cnpj("12.ABC.345/01DE-35"), "12ABC34501DE35")
		self.assertEqual(limpar_cnpj("12abc34501de35"), "12ABC34501DE35")

	def test_cnpj_numerico_formatado_valido(self):
		self.assertEqual(validar_cnpj("11.222.333/0001-81"), "11222333000181")

	def test_cnpj_numerico_digitos_valido(self):
		self.assertEqual(validar_cnpj("11222333000181"), "11222333000181")

	def test_cnpj_alfanumerico_oficial_receita(self):
		# Exemplo oficial RFB: 12.ABC.345/01DE-35
		self.assertEqual(_calcular_dv_cnpj("12ABC34501DE"), "35")
		self.assertEqual(validar_cnpj("12.ABC.345/01DE-35"), "12ABC34501DE35")
		self.assertEqual(validar_cnpj("12abc34501de35"), "12ABC34501DE35")

	def test_formatar_cnpj_alfanumerico(self):
		self.assertEqual(formatar_cnpj("12ABC34501DE35"), "12.ABC.345/01DE-35")
		self.assertEqual(formatar_cnpj("11222333000181"), "11.222.333/0001-81")

	def test_cnpj_dv_incorreto(self):
		with self.assertRaises(ValidationError):
			validar_cnpj("12.ABC.345/01DE-00")

	def test_cnpj_dv_nao_numerico(self):
		with self.assertRaises(ValidationError):
			validar_cnpj("12ABC34501DEAB")

	def test_cnpj_sequencia_invalida(self):
		with self.assertRaises(ValidationError):
			validar_cnpj("00.000.000/0000-00")

	def test_cnpj_curto_invalido(self):
		with self.assertRaises(ValidationError):
			validar_cnpj("123")

	def test_cnpj_vazio(self):
		self.assertEqual(validar_cnpj(""), "")
		self.assertEqual(validar_cnpj(None), "")
