import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def _ensure_event_custom_fields():
	create_custom_field(
		"Event",
		{
			"fieldname": "custom_source_doctype",
			"label": "Source DocType",
			"fieldtype": "Data",
			"hidden": 1,
			"no_copy": 1,
		},
	)
	create_custom_field(
		"Event",
		{
			"fieldname": "custom_source_name",
			"label": "Source Name",
			"fieldtype": "Data",
			"hidden": 1,
			"no_copy": 1,
		},
	)


def ensure_engenharia_roles():
	_ensure_roles()


def ensure_event_custom_fields():
	"""Idempotente — usado em after_install e after_migrate."""
	_ensure_event_custom_fields()
	frappe.clear_cache(doctype="Event")


def _ensure_roles():
	from engenharia.setup.roles import seed_roles

	seed_roles()


def after_install():
	_ensure_roles()
	ensure_event_custom_fields()
	from engenharia.setup.permissions import ensure_engenharia_permissions
	from engenharia.setup.seed import ensure_seed_data
	from engenharia.setup.translations import ensure_doctype_translations

	ensure_engenharia_permissions()
	ensure_seed_data()
	ensure_doctype_translations()
	frappe.db.commit()  # setup: seed de custom fields em Event durante install
