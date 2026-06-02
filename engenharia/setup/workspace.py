import os

import frappe


def ensure_engenharia_workspace():
	"""Sincroniza o Workspace Engenharia a partir do JSON do módulo (idempotente)."""
	path = frappe.get_app_path(
		"engenharia",
		"engenharia",
		"workspace",
		"engenharia",
		"engenharia.json",
	)
	if not os.path.exists(path):
		return

	frappe.import_doc(path)

	if frappe.db.exists("Workspace", "Engenharia"):
		frappe.db.set_value(
			"Workspace",
			"Engenharia",
			{"module": "Engenharia", "app": "engenharia", "public": 1},
			update_modified=False,
		)

	frappe.clear_cache()
	frappe.db.commit()  # setup: sincroniza workspace no migrate
