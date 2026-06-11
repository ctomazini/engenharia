"""Migra construction_project.building_type de Select para Link → Building Type."""

from __future__ import annotations

import frappe

from engenharia.setup.seed import DEFAULT_BUILDING_TYPES, ensure_default_building_types


def execute():
	if not frappe.db.table_exists("tabConstruction Project"):
		return

	ensure_default_building_types()

	project_meta = frappe.get_meta("Construction Project")
	building_type_field = project_meta.get_field("building_type")
	if not building_type_field or building_type_field.fieldtype != "Link":
		return

	known_types = set(DEFAULT_BUILDING_TYPES)
	for row in frappe.get_all(
		"Construction Project",
		fields=["name", "building_type"],
		filters={"building_type": ["is", "set"]},
		limit=0,
	):
		value = (row.building_type or "").strip()
		if not value:
			continue
		if frappe.db.exists("Building Type", value):
			continue

		if value not in known_types:
			frappe.get_doc(
				{"doctype": "Building Type", "building_type_name": value}
			).insert(ignore_permissions=True)  # patch: preserva tipos legados ad hoc
			known_types.add(value)

		frappe.db.set_value(
			"Construction Project",
			row.name,
			"building_type",
			value,
			update_modified=False,
		)

	frappe.db.commit()  # patch: migra valores legados de building_type
