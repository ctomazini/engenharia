"""Aplicação de templates de etapa em projetos."""

from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist()
def get_stage_count_for_project(project: str) -> int:
	"""Retorna contagem de etapas existentes no projeto."""
	frappe.has_permission("Construction Project", "read", throw=True)
	return frappe.db.count("Project Stage", {"project": project})


@frappe.whitelist()
def apply_template_to_project(project: str, project_type: str) -> dict:
	"""Aplica template de etapas ao projeto. Remove etapas existentes."""
	frappe.has_permission("Construction Project", "write", throw=True)
	frappe.has_permission("Project Stage", "create", throw=True)

	template_name = frappe.db.get_value(
		"Project Stage Template",
		{"project_type": project_type},
		"name",
	)
	if not template_name:
		frappe.msgprint(_("Nenhum template encontrado para o tipo {0}.").format(project_type))
		return {"created": 0}

	existing = frappe.get_all(
		"Project Stage",
		filters={"project": project},
		pluck="name",
		limit=500,
	)
	for name in existing:
		frappe.delete_doc(
			"Project Stage",
			name,
			ignore_permissions=True,  # permissão já validada acima
		)

	template = frappe.get_doc("Project Stage Template", template_name)
	created = 0
	for row in sorted(template.stages, key=lambda x: x.sort_order or 0):
		frappe.get_doc(
			{
				"doctype": "Project Stage",
				"project": project,
				"stage_type": row.stage_type,
				"weight": row.weight,
				"order": row.sort_order,
				"status": "Não iniciada",
				"progress": 0,
			}
		).insert(ignore_permissions=True)  # permissão já validada acima
		created += 1

	from engenharia.project_progress import sync_project_physical_progress

	sync_project_physical_progress(project)

	return {"created": created}


@frappe.whitelist()
def redistribute_stage_weights(project: str) -> dict:
	"""Redistribui pesos igualmente entre todas as etapas do projeto."""
	frappe.has_permission("Construction Project", "write", throw=True)

	stages = frappe.get_all(
		"Project Stage",
		filters={"project": project},
		fields=["name"],
		order_by="order asc",
		limit=500,
	)
	if not stages:
		return {"count": 0}

	n = len(stages)
	base = round(100 / n, 2)
	remainder = round(100 - (base * n), 2)

	for idx, stage in enumerate(stages):
		weight = base + (remainder if idx == n - 1 else 0)
		frappe.db.set_value("Project Stage", stage.name, "weight", weight, update_modified=False)

	from engenharia.project_progress import sync_project_physical_progress

	sync_project_physical_progress(project)

	return {"count": n}
