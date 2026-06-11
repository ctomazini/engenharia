"""Migra project_document.category de Select para Link → Document Category."""

from __future__ import annotations

import frappe

from engenharia.setup.seed import DEFAULT_DOCUMENT_CATEGORIES, ensure_default_document_categories


def execute():
	if not frappe.db.table_exists("tabProject Document"):
		return

	ensure_default_document_categories()

	meta = frappe.get_meta("Project Document")
	category_field = meta.get_field("category")
	if not category_field or category_field.fieldtype != "Link":
		return

	known = set(DEFAULT_DOCUMENT_CATEGORIES)
	for row in frappe.get_all(
		"Project Document",
		fields=["name", "category"],
		filters={"category": ["is", "set"]},
		limit=0,
	):
		value = (row.category or "").strip()
		if not value:
			continue
		if not frappe.db.exists("Document Category", value):
			frappe.get_doc(
				{"doctype": "Document Category", "category_name": value}
			).insert(ignore_permissions=True)  # patch: preserva categorias legadas ad hoc
			known.add(value)

		frappe.db.set_value(
			"Project Document",
			row.name,
			"category",
			value,
			update_modified=False,
		)

	frappe.db.commit()  # patch: migra valores legados de category
