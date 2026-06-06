import frappe
from frappe.model.document import Document
from frappe.utils import flt, today

from engenharia.titles import apply_title_post_insert, recompose_title


@frappe.whitelist()
def get_technical_items_for_select() -> list[dict]:
	frappe.has_permission("Technical Item", "read", throw=True)

	items = frappe.get_all(
		"Technical Item",
		fields=["name", "item_name", "category"],
		order_by="item_name asc",
		limit=100,
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


@frappe.whitelist()
def create_budget_revision(project: str) -> dict:
	frappe.has_permission("Construction Project", "write", doc=project, throw=True)

	doc = frappe.get_doc("Construction Project", project)
	current_total = flt(doc.spec_project_total)

	for row in doc.budget_revisions or []:
		if row.status == "Vigente":
			row.total_amount = current_total
			row.status = "Supersedida"

	new_revision = int(doc.budget_revision or 1) + 1
	doc.budget_revision = new_revision
	doc.append(
		"budget_revisions",
		{
			"revision_number": new_revision,
			"revision_date": today(),
			"total_amount": 0,
			"status": "Vigente",
		},
	)
	doc.save()

	return {"revision_number": new_revision}


class ConstructionProject(Document):
	def validate(self):
		recompose_title(self)
		self._sync_physical_progress()
		self._seed_initial_budget_revision()

	def _seed_initial_budget_revision(self) -> None:
		if self.budget_revisions:
			return

		self.budget_revision = self.budget_revision or 1
		self.append(
			"budget_revisions",
			{
				"revision_number": self.budget_revision,
				"revision_date": today(),
				"total_amount": 0,
				"status": "Vigente",
			},
		)

	def _sync_physical_progress(self):
		from engenharia.project_progress import calculate_physical_progress

		if self.is_new() or not self.name:
			self.physical_progress = 0
			return
		self.physical_progress = calculate_physical_progress(self.name)

	def after_insert(self):
		apply_title_post_insert(self)
