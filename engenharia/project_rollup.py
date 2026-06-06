"""Agregação de resultados de Project Item na Construction Project."""

from __future__ import annotations

import html

import frappe
from frappe.utils import cint, cstr, flt

from engenharia.formula_roles import PREVIEW_OUTPUT_ROLES


def on_project_item_change(doc, method=None):
	if not doc.project:
		return
	recompute_construction_project_specs(doc.project)


def _current_budget_revision(project: str) -> int:
	return cint(frappe.db.get_value("Construction Project", project, "budget_revision")) or 1


def recompute_construction_project_specs(project: str) -> None:
	frappe.has_permission("Construction Project", "read", doc=project, throw=True)

	current_revision = _current_budget_revision(project)
	items = frappe.get_all(
		"Project Item",
		filters={"project": project, "budget_revision": current_revision},
		fields=["total_value"],
		limit=500,
	)
	project_total = sum(flt(row.total_value) for row in items)

	frappe.db.set_value(
		"Construction Project",
		project,
		"spec_project_total",
		project_total,
		update_modified=False,
	)

	frappe.db.set_value(
		"Project Budget Revision",
		{
			"parent": project,
			"parenttype": "Construction Project",
			"revision_number": current_revision,
			"status": "Vigente",
		},
		"total_amount",
		project_total,
		update_modified=False,
	)


def build_spec_preview_html(project: str) -> str:
	frappe.has_permission("Construction Project", "read", doc=project, throw=True)

	current_revision = _current_budget_revision(project)
	items = frappe.get_all(
		"Project Item",
		filters={"project": project, "budget_revision": current_revision},
		fields=["name", "title"],
		limit=500,
	)
	if not items:
		return ""

	item_names = [row.name for row in items]
	outputs = frappe.get_all(
		"Project Item Output",
		filters={"parent": ["in", item_names], "role": ["in", list(PREVIEW_OUTPUT_ROLES)]},
		fields=["parent", "label", "value", "unit", "role"],
		limit=2000,
	)
	item_by_name = {row.name: row for row in items}
	preview_lines: list[str] = []
	for row in outputs:
		parent = item_by_name.get(row.parent)
		item_label = parent.title if parent else row.parent
		value = flt(row.value)
		unit = f" {row.unit}" if row.unit else ""
		preview_lines.append(
			f"<li><b>{html.escape(cstr(item_label))}</b>: "
			f"{html.escape(cstr(row.label))} = {value:.2f}{html.escape(unit)}</li>"
		)
	if not preview_lines:
		return ""
	return f'<ul class="list-unstyled">{"".join(preview_lines)}</ul>'


@frappe.whitelist()
def get_construction_project_spec_preview(project: str) -> dict:
	frappe.has_permission("Construction Project", "read", doc=project, throw=True)
	total = flt(frappe.db.get_value("Construction Project", project, "spec_project_total"))
	return {
		"preview_html": build_spec_preview_html(project),
		"project_total": total,
	}


@frappe.whitelist()
def get_project_items_summary(project: str) -> dict:
	"""Resumo tabular de Project Items para o form da obra."""
	frappe.has_permission("Construction Project", "read", doc=project, throw=True)

	current_revision = _current_budget_revision(project)
	items = frappe.get_all(
		"Project Item",
		filters={"project": project, "budget_revision": current_revision},
		fields=[
			"name",
			"title",
			"technical_item",
			"instance_label",
			"quantity",
			"unit",
			"unit_price",
			"total_value",
		],
		order_by="creation asc",
		limit=500,
	)
	if not items:
		return {"items": [], "project_total": 0}

	item_names = [row.name for row in items]
	params_by_parent: dict[str, list[dict]] = {name: [] for name in item_names}
	for row in frappe.get_all(
		"Project Item Parameter",
		filters={"parent": ["in", item_names]},
		fields=["parent", "label", "field_key", "value"],
		order_by="idx asc",
		limit=2000,
	):
		if row.value:
			params_by_parent.setdefault(row.parent, []).append(row)

	outputs_by_parent: dict[str, list[dict]] = {name: [] for name in item_names}
	for row in frappe.get_all(
		"Project Item Output",
		filters={
			"parent": ["in", item_names],
			"role": ["in", ["value", "volume", "area", "preview"]],
		},
		fields=["parent", "label", "value", "unit", "role"],
		order_by="idx asc",
		limit=2000,
	):
		outputs_by_parent.setdefault(row.parent, []).append(row)

	result_items = []
	for item in items:
		param_parts = []
		for param in params_by_parent.get(item.name, []):
			label = param.label or param.field_key
			param_parts.append(f"{label}={param.value}")
		output_parts = []
		for out in outputs_by_parent.get(item.name, []):
			unit = f" {out.unit}" if out.unit else ""
			output_parts.append(f"{out.label}={flt(out.value):.2f}{unit}")

		result_items.append(
			{
				"name": item.name,
				"title": item.title or item.technical_item,
				"technical_item": item.technical_item,
				"instance_label": item.instance_label,
				"quantity": flt(item.quantity or 1),
				"unit": item.unit,
				"unit_price": flt(item.unit_price),
				"total_value": flt(item.total_value),
				"params_summary": ", ".join(param_parts),
				"outputs_summary": "; ".join(output_parts),
			}
		)

	project_total = sum(flt(row["total_value"]) for row in result_items)
	return {"items": result_items, "project_total": project_total}


@frappe.whitelist()
def get_project_commission_summary(project: str) -> dict:
	"""Resumo de comissões vinculadas à obra."""
	frappe.has_permission("Construction Project", "read", doc=project, throw=True)

	rows = frappe.get_all(
		"Commission",
		filters={"construction_project": project, "status": ["!=", "Cancelled"]},
		fields=["name", "supplier_name", "total_value", "total_paid", "outstanding", "status"],
		limit=100,
	)
	total_value = sum(flt(row.total_value) for row in rows)
	total_paid = sum(flt(row.total_paid) for row in rows)
	outstanding = sum(flt(row.outstanding) for row in rows)
	active_count = sum(1 for row in rows if row.status in ("Open", "Partially Paid"))

	return {
		"count": len(rows),
		"active_count": active_count,
		"total_value": total_value,
		"total_paid": total_paid,
		"outstanding": outstanding,
	}
