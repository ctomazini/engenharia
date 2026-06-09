import frappe
from frappe import _
from frappe.utils import flt

from engenharia.engenharia.api.costs import (
	SOURCE_META,
	SOURCE_REIMBURSABLE,
	SOURCE_SUBCONTRACT,
	SOURCE_WORK_COST,
	build_consolidated_costs,
)
from engenharia.report_visuals import REPORT_COLORS, bar_chart, currency_summary, int_summary


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("project"):
		frappe.throw(_("Selecione uma obra."))

	columns = _get_columns()
	data, chart, report_summary = _get_data(filters)
	return columns, data, None, chart, report_summary


def _get_columns():
	return [
		{"fieldname": "date", "label": _("Data"), "fieldtype": "Date", "width": 100},
		{"fieldname": "source_label", "label": _("Tipo"), "fieldtype": "Data", "width": 130},
		{"fieldname": "category", "label": _("Categoria"), "fieldtype": "Data", "width": 140},
		{"fieldname": "description", "label": _("Descrição"), "fieldtype": "Data", "width": 220},
		{"fieldname": "supplier", "label": _("Fornecedor"), "fieldtype": "Data", "width": 140},
		{"fieldname": "stage", "label": _("Etapa"), "fieldtype": "Data", "width": 120},
		{"fieldname": "funded_by", "label": _("Quem arca"), "fieldtype": "Data", "width": 100},
		{"fieldname": "amount", "label": _("Valor"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "paid", "label": _("Pago"), "fieldtype": "Currency", "width": 110},
		{
			"fieldname": "outstanding",
			"label": _("Em aberto"),
			"fieldtype": "Currency",
			"width": 110,
		},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
		{
			"fieldname": "source_doctype",
			"label": _("DocType"),
			"fieldtype": "Data",
			"hidden": 1,
		},
		{
			"fieldname": "source_doc",
			"label": _("Documento"),
			"fieldtype": "Dynamic Link",
			"options": "source_doctype",
			"width": 150,
		},
	]


def _get_data(filters):
	payload = build_consolidated_costs(filters.project, filters)
	items = payload.get("items") or []
	summary = payload.get("summary") or {}

	data = []
	for row in items:
		data.append(
			{
				"date": row.get("date"),
				"source": row.get("source"),
				"source_label": row.get("source_label"),
				"category": row.get("category"),
				"description": row.get("description"),
				"supplier": row.get("supplier"),
				"stage": row.get("stage"),
				"funded_by": row.get("funded_by") or "",
				"amount": flt(row.get("amount")),
				"paid": flt(row.get("paid")),
				"outstanding": flt(row.get("outstanding")),
				"status": row.get("status"),
				"source_doc": row.get("name"),
				"source_doctype": row.get("source_doctype"),
			}
		)

	chart = _build_chart(items)
	report_summary = [
		currency_summary(summary.get("total_amount"), _("Total"), "Blue"),
		currency_summary(summary.get("total_paid"), _("Pago"), "Green"),
		currency_summary(summary.get("total_outstanding"), _("Em aberto"), "Orange"),
		int_summary(len(data), _("Lançamentos"), "Blue"),
	]
	return data, chart, report_summary


def _build_chart(items):
	if not items:
		return None

	categories: dict[str, dict[str, float]] = {}
	for row in items:
		category = row.get("category") or _("Sem categoria")
		source = row.get("source")
		bucket = categories.setdefault(
			category,
			{SOURCE_WORK_COST: 0, SOURCE_REIMBURSABLE: 0, SOURCE_SUBCONTRACT: 0},
		)
		bucket[source] = bucket.get(source, 0) + flt(row.get("amount"))

	sorted_categories = sorted(
		categories.items(),
		key=lambda item: sum(item[1].values()),
		reverse=True,
	)[:10]
	if not sorted_categories:
		return None

	labels = [label for label, _values in sorted_categories]
	datasets = []
	colors = []
	for source_key, color_key in (
		(SOURCE_WORK_COST, "blue"),
		(SOURCE_REIMBURSABLE, "orange"),
		(SOURCE_SUBCONTRACT, "green"),
	):
		datasets.append(
			{
				"name": SOURCE_META[source_key]["label"],
				"values": [values.get(source_key, 0) for _label, values in sorted_categories],
			}
		)
		colors.append(REPORT_COLORS[color_key])

	return bar_chart(labels, datasets, colors)
