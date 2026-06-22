import frappe
from frappe import _
from frappe.utils import flt

from engenharia.report_visuals import REPORT_COLORS, bar_chart, currency_summary, int_summary


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = _get_columns()
	data, chart, report_summary = _get_data(filters)
	return columns, data, None, chart, report_summary


def _get_columns():
	return [
		{"fieldname": "project_title", "label": _("Obra"), "fieldtype": "Data", "width": 280},
		{"fieldname": "total_cost", "label": _("Custo Total"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "entries", "label": _("Lançamentos"), "fieldtype": "Int", "width": 100},
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
	if filters.get("project"):
		query_filters["project"] = filters.project

	rows = frappe.get_all(
		"Work Cost",
		filters=query_filters,
		fields=["project", "amount"],
		limit_page_length=10000,
	)
	agg = {}
	for row in rows:
		bucket = agg.setdefault(row.project, {"total_cost": 0, "entries": 0})
		bucket["total_cost"] += flt(row.amount)
		bucket["entries"] += 1

	project_titles = {
		p.name: p.title
		for p in frappe.get_all("Construction Project", fields=["name", "title"], limit_page_length=10000)
	}
	total = sum(values["total_cost"] for values in agg.values())
	data = []
	for project, values in sorted(agg.items(), key=lambda item: item[1]["total_cost"], reverse=True):
		share = (values["total_cost"] / total * 100) if total else 0
		data.append(
			{
				"project": project,
				"project_title": project_titles.get(project, project),
				"total_cost": values["total_cost"],
				"entries": values["entries"],
				"share_percent": round(share, 1),
			}
		)

	chart = _build_chart(data)
	avg = (total / len(data)) if data else 0
	report_summary = [
		currency_summary(total, _("Custo Total"), "Red"),
		int_summary(len(data), _("Obras"), "Blue"),
		currency_summary(avg, _("Média por Obra"), "Orange"),
	]
	return data, chart, report_summary


def _build_chart(data):
	top = data[:10]
	if not top:
		return None

	labels = []
	values = []
	for row in top:
		title = row.get("project_title") or row.get("project")
		labels.append(title)
		values.append(flt(row.get("total_cost")))

	return bar_chart(
		labels,
		[{"name": _("Custo Total"), "values": values}],
		[REPORT_COLORS["red"]],
	)
