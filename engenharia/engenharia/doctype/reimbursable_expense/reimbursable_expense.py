import frappe
from frappe import _
from frappe.model.document import Document

from engenharia.titles import apply_title_post_insert, recompose_title


class ReimbursableExpense(Document):
	def validate(self):
		if not self.is_new() and frappe.db.get_value(self.doctype, self.name, "status") == "Cancelado":
			frappe.throw(_("Despesa cancelada não pode ser alterada."))

		if not self.customer and self.project:
			self.customer = frappe.db.get_value("Construction Project", self.project, "customer")
		if not self.customer:
			frappe.throw(_("Cliente é obrigatório. Selecione uma Obra válida."))

		if self.client_reimbursed_date and self.status == "A reembolsar":
			self.status = "Reembolsado"

		self._compose_title()

	def after_insert(self):
		apply_title_post_insert(self, use_description=True)

	def _compose_title(self):
		recompose_title(self, use_description=True)
