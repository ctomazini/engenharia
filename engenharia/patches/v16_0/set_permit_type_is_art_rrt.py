"""Marca tipos ART/RRT existentes no cadastro Permit Type."""

from __future__ import annotations

import frappe


def execute():
	if not frappe.db.table_exists("tabPermit Type"):
		return

	for type_name in ("ART/RRT", "ART", "RRT"):
		if frappe.db.exists("Permit Type", type_name):
			frappe.db.set_value("Permit Type", type_name, "is_art_rrt", 1, update_modified=False)

	frappe.db.commit()  # patch: flag is_art_rrt em tipos ART/RRT legados
