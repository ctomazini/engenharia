import frappe
from frappe import _
from frappe.model.document import Document

from engenharia.validators import validar_cnpj, validar_cpf, validar_email, validar_telefone


class Customer(Document):
	def before_save(self):
		if self.person_type == "Pessoa Física":
			self.trade_name = None
			self.cnpj = None
		else:
			self.cpf = None

	def validate(self):
		if self.person_type == "Pessoa Física":
			if not self.cpf:
				frappe.throw(
					_("CPF é obrigatório para Pessoa Física."),
					title=_("Campo obrigatório"),
				)
			self.cpf = validar_cpf(self.cpf)
		elif self.person_type == "Pessoa Jurídica":
			if not self.cnpj:
				frappe.throw(
					_("CNPJ é obrigatório para Pessoa Jurídica."),
					title=_("Campo obrigatório"),
				)
			self.cnpj = validar_cnpj(self.cnpj)

		if self.phone:
			tipo = "celular" if len((self.phone or "").replace(" ", "")) > 10 else "fixo"
			self.phone = validar_telefone(self.phone, tipo=tipo)
		if self.email:
			self.email = validar_email(self.email)

		self._validate_document_uniqueness()

	def _validate_document_uniqueness(self):
		if self.person_type == "Pessoa Física" and self.cpf:
			duplicate = frappe.db.exists(
				"Customer",
				{"cpf": self.cpf, "name": ["!=", self.name]},
			)
			if duplicate:
				frappe.throw(
					_("Já existe cliente cadastrado com o CPF {0}.").format(self.cpf),
					title=_("CPF duplicado"),
				)
		elif self.person_type == "Pessoa Jurídica" and self.cnpj:
			duplicate = frappe.db.exists(
				"Customer",
				{"cnpj": self.cnpj, "name": ["!=", self.name]},
			)
			if duplicate:
				frappe.throw(
					_("Já existe cliente cadastrado com o CNPJ {0}.").format(self.cnpj),
					title=_("CNPJ duplicado"),
				)
