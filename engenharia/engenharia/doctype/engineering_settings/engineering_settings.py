import frappe
from frappe import _
from frappe.model.document import Document

from engenharia.validators import validar_cnpj


class EngineeringSettings(Document):
	def validate(self):
		if self.company_cnpj:
			self.company_cnpj = validar_cnpj(self.company_cnpj)
