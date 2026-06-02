import frappe
from frappe import _
from frappe.model.document import Document

from engenharia.validators import validar_cnpj, validar_email, validar_telefone


class Supplier(Document):
	def validate(self):
		if self.cnpj:
			self.cnpj = validar_cnpj(self.cnpj)
		if self.phone:
			tipo = "celular" if len((self.phone or "").replace(" ", "")) > 10 else "fixo"
			self.phone = validar_telefone(self.phone, tipo=tipo)
		if self.email:
			self.email = validar_email(self.email)
