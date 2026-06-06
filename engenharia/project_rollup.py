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
