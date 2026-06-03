"""Migra permit.permit_type de Select para Link → Permit Type."""

from __future__ import annotations

import frappe

from engenharia.setup.seed import DEFAULT_PERMIT_TYPES, ensure_default_permit_types


def execute():
	if not frappe.db.table_exists("tabPermit"):
		return

	ensure_default_permit_types()

	permit_meta = frappe.get_meta("Permit")
	permit_type_field = permit_meta.get_field("permit_type")
	if not permit_type_field or permit_type_field.fieldtype != "Link":
		return

	known_types = set(DEFAULT_PERMIT_TYPES)
	for row in frappe.get_all("Permit", fields=["name", "permit_type"], limit_page_length=0):
		value = (row.permit_type or "").strip()
		if not value:
			continue
		if frappe.db.exists("Permit Type", value):
			continue

		if value not in known_types:
			frappe.get_doc({"doctype": "Permit Type", "type_name": value}).insert(
				ignore_permissions=True  # patch: preserva tipos legados ad hoc
			)
			known_types.add(value)

		frappe.db.set_value("Permit", row.name, "permit_type", value, update_modified=False)

	frappe.db.commit()  # patch: migra valores legados de permit_type
