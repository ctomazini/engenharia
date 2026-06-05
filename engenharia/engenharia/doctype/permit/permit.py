import frappe
from frappe import _
from frappe.model.document import Document

from engenharia.titles import apply_title_post_insert, recompose_title_if_empty


def permit_type_requires_art_rrt(permit_type: str | None) -> bool:
	if not permit_type or not frappe.db.exists("Permit Type", permit_type):
		return False
	return bool(frappe.db.get_value("Permit Type", permit_type, "is_art_rrt"))


class Permit(Document):
	def validate(self):
		if not self.customer and self.project:
			self.customer = frappe.db.get_value("Construction Project", self.project, "customer")
		if not self.customer:
			frappe.throw(_("Cliente é obrigatório. Selecione uma Obra válida."))

		if permit_type_requires_art_rrt(self.permit_type) and not self.art_rrt_number:
			frappe.throw(
				_("Nº ART/RRT é obrigatório para este tipo de protocolo."),
				title=_("Campo obrigatório"),
			)

		self._compose_title()

	def after_insert(self):
		apply_title_post_insert(self)

	def _compose_title(self):
		recompose_title_if_empty(self)
