import frappe
from frappe.permissions import add_permission, update_permission_property

ENGINHARIA_MODULE = "Engenharia"

USER_PERMISSIONS = {
	"read": 1,
	"write": 1,
	"create": 1,
	"delete": 0,
	"export": 1,
	"print": 1,
	"email": 1,
	"report": 1,
	"share": 1,
}

MANAGER_PERMISSIONS = {
	**USER_PERMISSIONS,
	"delete": 1,
}

PERM_PROPERTIES = (
	"read",
	"write",
	"create",
	"delete",
	"export",
	"print",
	"email",
	"report",
	"share",
)


def _role_has_permissions(doctype: str, role: str) -> bool:
	return bool(
		frappe.db.exists(
			"DocPerm",
			{"parent": doctype, "role": role, "permlevel": 0},
		)
	)


def _ensure_role_on_doctype(doctype: str, role: str, permissions: dict):
	if _role_has_permissions(doctype, role):
		return

	add_permission(doctype, role, permlevel=0)
	for prop in PERM_PROPERTIES:
		if prop in permissions:
			update_permission_property(doctype, role, 0, prop, permissions[prop])


def ensure_engenharia_permissions():
	"""Garante permissões Engenharia User/Manager em DocTypes do app."""
	doctypes = frappe.get_all(
		"DocType",
		filters={"module": ENGINHARIA_MODULE, "custom": 0},
		pluck="name",
	)
	for doctype in doctypes:
		_ensure_role_on_doctype(doctype, "Engenharia User", USER_PERMISSIONS)
		_ensure_role_on_doctype(doctype, "Engenharia Manager", MANAGER_PERMISSIONS)

	frappe.clear_cache(doctype="DocType")
	frappe.db.commit()  # setup: sincroniza permissões no migrate
