import frappe
from frappe import _
from frappe.utils import flt

from engenharia.report_visuals import (
	REPORT_COLORS,
	bar_chart,
	currency_summary,
	int_summary,
)

CATEGORY_PALETTE = [
	REPORT_COLORS["teal"],
	REPORT_COLORS["blue"],
	REPORT_COLORS["purple"],
	REPORT_COLORS["orange"],
	REPORT_COLORS["green"],
	REPORT_COLORS["amber"],
	REPORT_COLORS["red"],
	REPORT_COLORS["slate"],
]


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = _get_columns()
	data, chart, report_summary = _get_data(filters)
	return columns, data, None, chart, report_summary


def _get_columns():
	return [
		{"fieldname": "category_name", "label": _("Categoria"), "fieldtype": "Data", "width": 280},
		{"fieldname": "total_cost", "label": _("Custo Total"), "fieldtype": "Currency", "width": 140},
		{
			"fieldname": "share_percent",
			"label": _("% do Total"),
			"fieldtype": "Percent",
			"width": 110,
			"precision": 1,
		},
	]


def _get_data(filters):
	query_filters = {"status": ["!=", "Cancelled"]}
	if filters.get("cost_category"):
		query_filters["cost_category"] = filters.cost_category

	rows = frappe.get_all(
		"Work Cost",
		filters=query_filters,
		fields=["cost_category", "amount"],
		limit=0,
	)
	agg = {}
	for row in rows:
		key = row.cost_category or _("Sem categoria")
		agg[key] = agg.get(key, 0) + flt(row.amount)

	category_names = {
		c.name: c.category_name
		for c in frappe.get_all("Cost Category", fields=["name", "category_name"], limit=0)
	}
	total = sum(agg.values())
	data = []
	for key, value in sorted(agg.items(), key=lambda item: item[1], reverse=True):
		share = (value / total * 100) if total else 0
		data.append(
			{
				"cost_category": key if key != _("Sem categoria") else None,
				"category_name": category_names.get(key, key),
				"total_cost": value,
				"share_percent": round(share, 1),
			}
		)

	chart = _build_chart(data)
	top_name = data[0]["category_name"] if data else "—"
	report_summary = [
		currency_summary(total, _("Custo Total"), "Red"),
		int_summary(len(data), _("Categorias"), "Blue"),
		currency_summary(data[0]["total_cost"] if data else 0, _("Maior: {0}").format(top_name), "Orange"),
	]
	return data, chart, report_summary


def _build_chart(data):
	if not data:
		return None

	labels = [row["category_name"] for row in data[:8]]
	values = [flt(row["total_cost"]) for row in data[:8]]
	colors = [CATEGORY_PALETTE[i % len(CATEGORY_PALETTE)] for i in range(len(labels))]
	return bar_chart(
		labels,
		[{"name": _("Custo Total"), "values": values}],
		colors,
	)
