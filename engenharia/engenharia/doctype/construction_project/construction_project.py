import frappe
from frappe.model.document import Document
from frappe.utils import flt, today

from engenharia.titles import apply_title_post_insert, get_customer_name, recompose_title


def format_construction_project_link_label(doc=None, project_name=None):
	"""Label amigável para Link / autocomplete de obra."""
	if doc is None and project_name:
		doc = frappe.db.get_value(
			"Construction Project",
			project_name,
			["name", "title", "customer", "city", "status"],
			as_dict=True,
		)
	if not doc:
		return project_name or ""
	title = (doc.get("title") or doc.get("name") or "").strip()
	if title:
		return title
	customer = get_customer_name(doc.get("customer"))
	parts = [p for p in (customer, doc.get("city")) if p]
	return " - ".join(parts) if parts else doc.get("name") or ""


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def construction_project_query(
	doctype: str,
	txt: str,
	searchfield: str,
	start: int,
	page_len: int,
	filters,
) -> list[tuple[str, str]]:
	frappe.has_permission("Construction Project", "read", throw=True)
	txt = (txt or "").strip()
	list_filters = dict(filters or {})

	or_filters = [
		["name", "like", f"%{txt}%"],
		["title", "like", f"%{txt}%"],
		["customer", "like", f"%{txt}%"],
		["city", "like", f"%{txt}%"],
		["status", "like", f"%{txt}%"],
	]

	if txt:
		customers = frappe.get_all(
			"Customer",
			filters={"customer_name": ["like", f"%{txt}%"]},
			pluck="name",
			limit_page_length=50,
		)
		if customers:
			or_filters.append(["customer", "in", customers])

	rows = frappe.get_all(
		"Construction Project",
		filters=list_filters,
		or_filters=or_filters if txt else None,
		fields=["name", "title", "customer", "city", "status"],
		limit_start=start,
		limit_page_length=page_len,
		order_by="modified desc",
	)

	return [(row.name, format_construction_project_link_label(doc=row)) for row in rows]


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
