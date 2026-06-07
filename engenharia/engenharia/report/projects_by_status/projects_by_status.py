import frappe
from frappe import _

from engenharia.report_visuals import (
	PROJECT_STATUS_COLORS,
	donut_chart,
	int_summary,
)


def execute(filters=None):
	columns = _get_columns()
	data, chart, report_summary = _get_data()
	return columns, data, None, chart, report_summary


def _get_columns():
	return [
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 140},
		{"fieldname": "count", "label": _("Quantidade"), "fieldtype": "Int", "width": 120},
		{
			"fieldname": "share_percent",
			"label": _("% do Total"),
			"fieldtype": "Percent",
			"width": 110,
			"precision": 1,
		},
	]


def _get_data():
	statuses = ["Orçamento", "Em andamento", "Paralisada", "Concluída", "Cancelada"]
	data = []
	total = 0
	for status in statuses:
		count = frappe.db.count("Construction Project", {"status": status})
		total += count
		data.append({"status": status, "count": count, "share_percent": 0})

	for row in data:
		row["share_percent"] = round((row["count"] / total * 100), 1) if total else 0

	chart = _build_chart(data)
	active = next((r["count"] for r in data if r["status"] == "Em andamento"), 0)
	budget = next((r["count"] for r in data if r["status"] == "Orçamento"), 0)
	done = next((r["count"] for r in data if r["status"] == "Concluída"), 0)
	report_summary = [
		int_summary(total, _("Total de Obras"), "Blue"),
		int_summary(active, _("Em Andamento"), "Green"),
		int_summary(budget, _("Em Orçamento"), "Orange"),
		int_summary(done, _("Concluídas"), "Green"),
	]
	return data, chart, report_summary


def _build_chart(data):
	rows = [row for row in data if row["count"]]
	if not rows:
		return None

	labels = [row["status"] for row in rows]
	values = [row["count"] for row in rows]
	colors = [PROJECT_STATUS_COLORS.get(status, "#64748b") for status in labels]
	return donut_chart(labels, values, colors)
