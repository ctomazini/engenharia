"""Helpers for technical specification templates and project instances."""

import re

import frappe
from frappe import _
from frappe.utils import cstr

FIELD_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def _row_get(row, fieldname: str):
	if isinstance(row, dict):
		return row.get(fieldname)
	return getattr(row, fieldname, None)


def slugify_item_key(value: str) -> str:
	from frappe.modules import scrub

	return scrub(cstr(value)).replace("-", "_")


def validate_field_key(field_key: str, *, title: str | None = None):
	key = cstr(field_key).strip()
	if not key:
		frappe.throw(_("Chave do campo é obrigatória."), title=title or _("Campo inválido"))
	if not FIELD_KEY_PATTERN.match(key):
		frappe.throw(
			_("Chave {0} inválida. Use letras minúsculas, números e underscore (ex.: useful_height).").format(
				key
			),
			title=title or _("Campo inválido"),
		)
	return key


def get_technical_item_field_rows(technical_item: str) -> list[dict]:
	if not technical_item:
		return []
	return frappe.get_all(
		"Technical Item Field",
		filters={"parent": technical_item},
		fields=[
			"field_key",
			"label",
			"unit",
			"data_type",
			"default_value",
			"required",
			"sort_order",
		],
		order_by="sort_order asc, idx asc",
		limit=100,
	)


def expand_specification_template(spec_row, template_fields: list[dict] | None = None) -> list[dict]:
	"""Expande um item técnico em linhas planas (uma por campo do template)."""
	if not spec_row.technical_item:
		return []

	template_fields = template_fields or get_technical_item_field_rows(spec_row.technical_item)
	if not template_fields:
		frappe.throw(
			_("O item técnico {0} não possui campos definidos no cadastro.").format(spec_row.technical_item),
			title=_("Template incompleto"),
		)

	instance_label = cstr(_row_get(spec_row, "instance_label")).strip() or spec_row.technical_item
	stage = _row_get(spec_row, "stage")
	remarks = _row_get(spec_row, "remarks")
	existing_value = cstr(_row_get(spec_row, "value")).strip()

	rows = []
	for index, template in enumerate(template_fields):
		field_key = validate_field_key(template.field_key, title=_("Template inválido"))
		value = existing_value if index == 0 and existing_value else None
		rows.append(
			{
				"technical_item": spec_row.technical_item,
				"instance_label": instance_label,
				"stage": stage,
				"field_key": field_key,
				"label": template.label,
				"unit": template.unit,
				"data_type": template.data_type,
				"required": template.required,
				"value": value,
				"remarks": remarks if index == 0 else None,
			}
		)
	return rows
