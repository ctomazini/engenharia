"""Migra linhas planas de Project Specification para documentos Project Item."""

from __future__ import annotations

from collections import defaultdict

import frappe
from frappe.utils import cstr


def execute():
	if not frappe.db.table_exists("tabProject Specification"):
		return

	rows = frappe.get_all(
		"Project Specification",
		fields=[
			"name",
			"parent",
			"technical_item",
			"instance_label",
			"stage",
			"field_key",
			"label",
			"value",
			"unit",
			"data_type",
			"required",
		],
		limit_page_length=0,
	)
	if not rows:
		return

	grouped: dict[tuple, list] = defaultdict(list)
	for row in rows:
		if not (row.technical_item and row.field_key):
			continue
		key = (
			row.parent,
			row.technical_item,
			cstr(row.instance_label).strip() or row.technical_item,
		)
		grouped[key].append(row)

	for (project, technical_item, instance_label), spec_rows in grouped.items():
		if _project_item_exists(project, technical_item, instance_label):
			continue

		doc = frappe.new_doc("Project Item")
		doc.update(
			{
				"project": project,
				"technical_item": technical_item,
				"instance_label": instance_label,
				"stage": spec_rows[0].stage,
				"quantity": 1,
			}
		)
		for spec in spec_rows:
			doc.append(
				"parameter_values",
				{
					"field_key": spec.field_key,
					"label": spec.label,
					"value": spec.value,
					"unit": spec.unit,
					"data_type": spec.data_type,
					"required": spec.required,
				},
			)
		doc.insert(ignore_permissions=True)  # migrate: conversão legado Project Specification

	for row in rows:
		if row.name:
			frappe.delete_doc("Project Specification", row.name, force=1, ignore_permissions=True)


def _project_item_exists(project: str, technical_item: str, instance_label: str) -> bool:
	return bool(
		frappe.db.exists(
			"Project Item",
			{
				"project": project,
				"technical_item": technical_item,
				"instance_label": instance_label,
			},
		)
	)
