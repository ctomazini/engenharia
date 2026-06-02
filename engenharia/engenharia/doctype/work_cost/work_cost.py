import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from engenharia.titles import apply_title_post_insert, recompose_title_if_empty


class WorkCost(Document):
	def validate(self):
		if not self.is_new() and frappe.db.get_value(self.doctype, self.name, "status") == "Cancelado":
			frappe.throw(_("Custo cancelado não pode ser alterado."))

		if flt(self.amount) <= 0:
			frappe.throw(_("Valor deve ser maior que zero."))

		self._compose_title()

	def after_insert(self):
		apply_title_post_insert(self, use_description=True)

	def _compose_title(self):
		recompose_title_if_empty(self, use_description=True)
