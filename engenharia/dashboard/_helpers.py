import frappe
from frappe.utils import cint, flt, getdate, today

LIST_LIMIT_MAX = 100
DEFAULT_LIST_LIMIT_KEYS = (
	"timeline",
	"payments",
	"parcelas",
	"despesas",
	"comunicacoes",
	"deadlines",
	"tasks",
	"operational",
)


def _names_lookup(doctype, names, name_field):
	names = list({name for name in names if name})
	if not names:
		return {}
	rows = frappe.get_all(doctype, filters={"name": ["in", names]}, fields=["name", name_field])
	return {row.name: row.get(name_field) or row.name for row in rows}


def _customer_name_lookup(customer_names):
	return _names_lookup("Customer", customer_names, "customer_name")


def _project_lookup(project_names):
	names = list({name for name in project_names if name})
	if not names:
		return {}
	rows = frappe.get_all(
		"Construction Project",
		filters={"name": ["in", names]},
		fields=["name", "title", "customer", "status"],
	)
	return {row.name: row for row in rows}


def _normalize_period_days(period_days):
	days = cint(period_days or 7)
	if days not in (1, 7, 15, 30):
		days = 7
	return days


def _normalize_list_limits(list_limits=None, list_limit=None):
	defaults = {key: 5 for key in DEFAULT_LIST_LIMIT_KEYS}
	parsed = {}
	if list_limits:
		if isinstance(list_limits, str):
			parsed = frappe.parse_json(list_limits) or {}
		elif isinstance(list_limits, dict):
			parsed = list_limits

	legacy = cint(list_limit) if list_limit is not None else None
	normalized = {}
	for key in DEFAULT_LIST_LIMIT_KEYS:
		if key in parsed:
			val = cint(parsed[key])
			normalized[key] = val if val in (5, 10, 15) else 5
		elif legacy is not None and legacy in (5, 10, 15):
			normalized[key] = legacy
		else:
			normalized[key] = defaults[key]
	return normalized


def _list_cap(list_limits, key):
	val = list_limits.get(key, 5)
	return LIST_LIMIT_MAX if not val else min(val, LIST_LIMIT_MAX)


def user_is_engenharia_manager():
	roles = set(frappe.get_roles())
	return bool(roles & {"Engenharia Manager", "System Manager", "Administrator"})
