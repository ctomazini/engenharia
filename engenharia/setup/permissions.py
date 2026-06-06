import frappe
from frappe.permissions import setup_custom_perms
from frappe.utils import cint

ENGINHARIA_MODULE = "Engenharia"
ROLE_USER = "Engenharia User"
ROLE_MANAGER = "Engenharia Manager"

PERM_PROPERTIES = (
	"read",
	"write",
	"create",
	"delete",
	"import",
	"export",
	"print",
	"email",
	"report",
	"share",
)

MANAGER_FULL = {
	"read": 1,
	"write": 1,
	"create": 1,
	"delete": 1,
	"import": 1,
	"export": 1,
	"print": 1,
	"email": 1,
	"report": 1,
	"share": 1,
}

USER_OPERATIONAL = {
	"read": 1,
	"write": 1,
	"create": 1,
	"delete": 0,
	"import": 1,
	"export": 1,
	"print": 1,
	"email": 1,
	"report": 1,
	"share": 1,
}

USER_READ = {
	"read": 1,
	"write": 0,
	"create": 0,
	"delete": 0,
	"import": 0,
	"export": 1,
	"print": 1,
	"email": 1,
	"report": 1,
	"share": 0,
}

MANAGER_FINANCIAL_PERMLEVEL = {
	"read": 1,
	"write": 1,
	"create": 0,
	"delete": 0,
	"import": 0,
	"export": 0,
	"print": 0,
	"email": 0,
	"report": 0,
	"share": 0,
}

FINANCIAL_DOCTYPES = frozenset(
	{
		"Commission",
		"Engineering Contract",
		"Engineering Settings",
		"Payment",
		"Project Specification",
		"Reimbursable Expense",
		"Work Cost",
	}
)

CATALOG_DOCTYPES = frozenset(
	{
		"Cost Category",
		"Document Kit",
		"Document Template",
		"Permit Type",
		"Public Agency",
		"Stage Type",
		"Supplier",
		"Technical Item",
	}
)

OPERATIONAL_DOCTYPES = frozenset(
	{
		"Communication Log",
		"Construction Measurement",
		"Construction Project",
		"Customer",
		"Deadline",
		"Permit",
		"Project Item",
		"Project Stage",
		"Task",
		"Time Log",
	}
)

MANAGED_DOCTYPES = FINANCIAL_DOCTYPES | CATALOG_DOCTYPES | OPERATIONAL_DOCTYPES


def _clear_engenharia_role_perms(doctype: str, role: str):
	frappe.db.delete(
		"Custom DocPerm",
		{"parent": doctype, "role": role, "if_owner": 0},
	)
	frappe.db.delete("DocPerm", {"parent": doctype, "role": role})


def _upsert_custom_docperm(doctype: str, role: str, permlevel: int, permissions: dict):
	setup_custom_perms(doctype)
	filters = {"parent": doctype, "role": role, "permlevel": permlevel, "if_owner": 0}
	row = {prop: cint(permissions.get(prop, 0)) for prop in PERM_PROPERTIES}
	existing = frappe.db.get_value("Custom DocPerm", filters, "name")
	if existing:
		frappe.db.set_value("Custom DocPerm", existing, row, update_modified=False)
		return

	doc = {
		"doctype": "Custom DocPerm",
		"parent": doctype,
		"parenttype": "DocType",
		"parentfield": "permissions",
		"role": role,
		"permlevel": permlevel,
		"if_owner": 0,
		**row,
	}
	frappe.get_doc(doc).insert(ignore_permissions=True)


def _validate_doctype_permissions(doctype: str):
	from frappe.core.doctype.doctype.doctype import validate_permissions_for_doctype

	validate_permissions_for_doctype(doctype)


def _apply_construction_project_perms():
	doctype = "Construction Project"
	_clear_engenharia_role_perms(doctype, ROLE_MANAGER)
	_clear_engenharia_role_perms(doctype, ROLE_USER)
	_upsert_custom_docperm(doctype, ROLE_MANAGER, 0, MANAGER_FULL)
	_upsert_custom_docperm(doctype, ROLE_MANAGER, 1, MANAGER_FINANCIAL_PERMLEVEL)
	_upsert_custom_docperm(doctype, ROLE_USER, 0, USER_OPERATIONAL)
	_validate_doctype_permissions(doctype)


def _apply_doctype_perms(doctype: str):
	if doctype == "Construction Project":
		_apply_construction_project_perms()
		return

	_clear_engenharia_role_perms(doctype, ROLE_MANAGER)
	_clear_engenharia_role_perms(doctype, ROLE_USER)

	if doctype in FINANCIAL_DOCTYPES:
		_upsert_custom_docperm(doctype, ROLE_MANAGER, 0, MANAGER_FULL)
	elif doctype in CATALOG_DOCTYPES:
		_upsert_custom_docperm(doctype, ROLE_MANAGER, 0, MANAGER_FULL)
		_upsert_custom_docperm(doctype, ROLE_USER, 0, USER_READ)
	elif doctype in OPERATIONAL_DOCTYPES:
		_upsert_custom_docperm(doctype, ROLE_MANAGER, 0, MANAGER_FULL)
		_upsert_custom_docperm(doctype, ROLE_USER, 0, USER_OPERATIONAL)

	_validate_doctype_permissions(doctype)


def ensure_engenharia_permissions():
	"""Sincroniza permissões Engenharia User/Manager conforme matriz O/F/C."""
	for doctype in sorted(MANAGED_DOCTYPES):
		_apply_doctype_perms(doctype)

	frappe.clear_cache(doctype="DocType")
	frappe.db.commit()  # setup: sincroniza permissões no migrate
