import frappe
from frappe import _
from frappe.model.document import Document

from engenharia.titles import apply_title_post_insert, recompose_title


class Deadline(Document):
	def validate(self):
		if not self.customer and self.project:
			self.customer = frappe.db.get_value("Construction Project", self.project, "customer")
		if not self.customer:
			frappe.throw(_("Cliente é obrigatório. Selecione uma Obra válida."))
		if self.deadline_type == "Órgão" and not self.public_agency:
			frappe.throw(_("Órgão Público é obrigatório quando o tipo é Órgão."))
		self._compose_title()

	def after_insert(self):
		apply_title_post_insert(self)

	def _compose_title(self):
		recompose_title(self)


@frappe.whitelist()
def get_events(
	start: str,
	end: str,
	filters: str | dict | None = None,
	doctype: str | None = None,
	field_map: str | dict | None = None,
	fields: str | list | None = None,
):
	"""Eventos do calendário para Deadline."""
	if not frappe.has_permission("Deadline", "read"):
		frappe.throw(_("Not Permitted"), frappe.PermissionError)

	filter_list = [["due_date", "between", [start, end]]]
	if filters:
		parsed = frappe.parse_json(filters) if isinstance(filters, str) else filters
		if parsed:
			filter_list.extend(parsed)

	return frappe.get_all(
		"Deadline",
		filters=filter_list,
		fields=[
			"name",
			"due_date",
			"description",
			"title",
			"customer",
			"project",
			"status",
			"priority",
		],
		order_by="due_date asc",
		limit=500,
	)
