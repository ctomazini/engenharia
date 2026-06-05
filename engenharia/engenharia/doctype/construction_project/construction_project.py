import frappe
from frappe.model.document import Document


@frappe.whitelist()
def get_technical_items_for_select() -> list[dict]:
	frappe.has_permission("Technical Item", "read", throw=True)

	items = frappe.get_all(
		"Technical Item",
		fields=["name", "item_name", "category"],
		order_by="item_name asc",
		limit_page_length=100,
	)
	result: list[dict] = []
	for item in items:
		if frappe.db.count("Technical Item Field", {"parent": item.name}):
			result.append(item)
	return result


@frappe.whitelist()
def create_project_item(
	project: str,
	technical_item: str,
	instance_label: str | None = None,
	stage: str | None = None,
) -> str:
	frappe.has_permission("Project Item", "create", throw=True)
	frappe.has_permission("Construction Project", "write", doc=project, throw=True)

	from engenharia.engenharia.doctype.project_item.project_item import (
		build_parameter_rows_from_template,
	)

	template = frappe.get_doc("Technical Item", technical_item)
	doc = frappe.new_doc("Project Item")
	doc.update(
		{
			"project": project,
			"technical_item": technical_item,
			"instance_label": instance_label,
			"stage": stage,
		}
	)
	for row in build_parameter_rows_from_template(technical_item):
		doc.append("parameter_values", row)
	if not doc.instance_label:
		doc.instance_label = template.item_name
	doc.flags.ignore_required_parameters = True
	doc.insert()
	return doc.name


class ConstructionProject(Document):
	def validate(self):
		self._compose_title()
		self._sync_physical_progress()

	def _sync_physical_progress(self):
		from engenharia.project_progress import calculate_physical_progress

		if self.is_new() or not self.name:
			self.physical_progress = 0
			return
		self.physical_progress = calculate_physical_progress(self.name)

	def _compose_title(self):
		from engenharia.titles import recompose_title

		recompose_title(self)

	def after_insert(self):
		from engenharia.titles import apply_title_post_insert

		apply_title_post_insert(self)
