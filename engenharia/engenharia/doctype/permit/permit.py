import frappe
from frappe import _
from frappe.model.document import Document

from engenharia.titles import apply_title_post_insert, recompose_title_if_empty


class Permit(Document):
	def validate(self):
		if not self.customer and self.project:
			self.customer = frappe.db.get_value("Construction Project", self.project, "customer")
		if not self.customer:
			frappe.throw(_("Cliente é obrigatório. Selecione uma Obra válida."))
		self._compose_title()

	def after_insert(self):
		apply_title_post_insert(self)

	def _compose_title(self):
		recompose_title_if_empty(self)
