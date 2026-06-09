import frappe
from frappe import _
from frappe.utils import flt

from engenharia.engenharia.api.costs import build_consolidated_costs_summary
from engenharia.report_visuals import REPORT_COLORS, bar_chart, currency_summary, int_summary, percent_summary


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = _get_columns()
	data, chart, report_summary = _get_data(filters)
	return columns, data, None, chart, report_summary


def _get_columns():
	return [
		{
			"fieldname": "project",
			"label": _("Obra"),
			"fieldtype": "Link",
			"options": "Construction Project",
			"width": 140,
		},
		{"fieldname": "project_title", "label": _("Título"), "fieldtype": "Data", "width": 240},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 110},
		{"fieldname": "budget_total", "label": _("Orçado"), "fieldtype": "Currency", "width": 130},
		{
			"fieldname": "realized_committed",
			"label": _("Realizado (comprometido)"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "realized_paid",
			"label": _("Realizado (pago)"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "realized_outstanding",
			"label": _("Em aberto"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "budget_variance",
			"label": _("Saldo do orçamento"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "budget_used_percent",
			"label": _("% orçamento usado"),
			"fieldtype": "Percent",
			"width": 120,
			"precision": 1,
		},
	]


def _get_data(filters):
	project_filters: dict = {}
	if filters.get("project"):
		project_filters["name"] = filters.project
	if filters.get("status"):
		project_filters["status"] = filters.status

	projects = frappe.get_all(
		"Construction Project",
		filters=project_filters,
		fields=["name", "title", "status", "spec_project_total"],
		limit=500,
	)

	data = []
	total_budget = 0.0
	total_committed = 0.0
	total_paid = 0.0
	used_pcts: list[float] = []
	over_budget_count = 0

	for project in projects:
		budget = flt(project.spec_project_total)
		summary = build_consolidated_costs_summary(project.name)
		committed = flt(summary.get("total_amount"))
		paid = flt(summary.get("total_paid"))
		outstanding = flt(summary.get("total_outstanding"))

		if not budget and not committed:
			continue

		variance = budget - committed
		used_pct = round((committed / budget * 100), 1) if budget else 0

		if budget and committed > budget:
			over_budget_count += 1

		data.append(
			{
				"project": project.name,
				"project_title": project.title or project.name,
				"status": project.status,
				"budget_total": budget,
				"realized_committed": committed,
				"realized_paid": paid,
				"realized_outstanding": outstanding,
				"budget_variance": variance,
				"budget_used_percent": used_pct,
			}
		)
		total_budget += budget
		total_committed += committed
		total_paid += paid
		if budget:
			used_pcts.append(used_pct)

	data.sort(key=lambda row: row["budget_used_percent"], reverse=True)

	chart = _build_chart(data)
	avg_used = round(sum(used_pcts) / len(used_pcts), 1) if used_pcts else 0
	report_summary = [
		currency_summary(total_budget, _("Total orçado"), "Blue"),
		currency_summary(total_committed, _("Total realizado"), "Orange"),
		currency_summary(total_budget - total_committed, _("Saldo orçamento"), "Green"),
		currency_summary(total_paid, _("Total pago"), "Green"),
		int_summary(over_budget_count, _("Obras acima do orçamento"), "Red"),
		percent_summary(avg_used, _("% orçamento usado (média)"), "Blue"),
	]
	return data, chart, report_summary


def _build_chart(data):
	candidates = [row for row in data if flt(row.get("budget_total")) > 0]
	top = sorted(candidates, key=lambda row: flt(row.get("realized_committed")), reverse=True)[:10]
	if not top:
		return None

	labels = [row.get("project_title") or row.get("project") for row in top]
	return bar_chart(
		labels,
		[
			{"name": _("Orçado"), "values": [flt(row.get("budget_total")) for row in top]},
			{
				"name": _("Realizado (comprometido)"),
				"values": [flt(row.get("realized_committed")) for row in top],
			},
		],
		[REPORT_COLORS["blue"], REPORT_COLORS["orange"]],
	)
