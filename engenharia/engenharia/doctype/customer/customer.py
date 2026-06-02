import frappe
from frappe import _
from frappe.model.document import Document

from engenharia.validators import limpar_numerico, validar_cnpj, validar_cpf, validar_email, validar_telefone


class Customer(Document):
	def before_save(self):
		if self.person_type == "Pessoa Física":
			self.trade_name = None
			self.legal_representative = None
			self.legal_representative_role = None
			self.legal_representative_cpf = None
			self.legal_representative_nationality = None
			self.cnpj = None
		else:
			self.cpf = None
			self.rg = None
			self.marital_status = None
			self.profession = None
			self.nationality = None

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
			if self.legal_representative_cpf:
				self.legal_representative_cpf = validar_cpf(self.legal_representative_cpf)

		self._validate_document_uniqueness()
		self._validate_contacts()
		self._validate_addresses()

	def _validate_contacts(self):
		for contact in self.contacts or []:
			if contact.phone:
				contact.phone = validar_telefone(contact.phone, tipo="fixo")
			if contact.mobile:
				contact.mobile = validar_telefone(contact.mobile, tipo="celular")
			if contact.email:
				contact.email = validar_email(contact.email)

	def _validate_addresses(self):
		for address in self.addresses or []:
			if address.cep:
				address.cep = limpar_numerico(address.cep)

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
