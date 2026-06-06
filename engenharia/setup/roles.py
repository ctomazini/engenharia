import frappe

ROLES = ("Engenharia User", "Engenharia Manager")


def seed_roles():
	"""Seed idempotente dos roles do app."""
	for role_name in ROLES:
		if frappe.db.exists("Role", role_name):
			continue
		doc = {
			"doctype": "Role",
			"role_name": role_name,
			"is_custom": 1,
		}
		if frappe.get_meta("Role").has_field("desk_access"):
			doc["desk_access"] = 1
		frappe.get_doc(doc).insert(ignore_permissions=True)  # setup: cria roles durante migrate
