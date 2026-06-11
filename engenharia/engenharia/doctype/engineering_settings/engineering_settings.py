import frappe
from frappe import _
from frappe.model.document import Document

from engenharia.validators import limpar_numerico, validar_cnpj, validar_cpf, validar_email, validar_telefone


class EngineeringSettings(Document):
	def validate(self):
		if self.company_cnpj:
			self.company_cnpj = validar_cnpj(self.company_cnpj)
		if self.engineer_cpf:
			self.engineer_cpf = validar_cpf(self.engineer_cpf)
		if self.engineer_phone:
			tipo = "celular" if len(limpar_numerico(self.engineer_phone)) >= 11 else "fixo"
			self.engineer_phone = validar_telefone(self.engineer_phone, tipo=tipo)
		if self.engineer_email:
			self.engineer_email = validar_email(self.engineer_email)
