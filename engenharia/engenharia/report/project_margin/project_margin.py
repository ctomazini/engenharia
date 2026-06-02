import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = [
		{"fieldname": "project", "label": _("Obra"), "fieldtype": "Link", "options": "Construction Project", "width": 180},
		{"fieldname": "project_title", "label": _("Título"), "fieldtype": "Data", "width": 220},
		{"fieldname": "contract_value", "label": _("Contrato"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_cost", "label": _("Custos"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "margin", "label": _("Margem"), "fieldtype": "Currency", "width": 130},
	]
	contracts = frappe.get_all(
		"Engineering Contract",
		filters={"status": ["!=", "Cancelado"]},
		fields=["project", "current_value"],
		limit=0,
	)
	contract_by_project = {}
	for row in contracts:
		contract_by_project[row.project] = contract_by_project.get(row.project, 0) + flt(row.current_value)

	costs = frappe.get_all(
		"Work Cost",
		filters={"status": ["!=", "Cancelado"]},
		fields=["project", "amount"],
		limit=0,
	)
	cost_by_project = {}
	for row in costs:
		cost_by_project[row.project] = cost_by_project.get(row.project, 0) + flt(row.amount)

	project_titles = {
		p.name: p.title
		for p in frappe.get_all("Construction Project", fields=["name", "title"], limit=0)
	}
	projects = set(contract_by_project) | set(cost_by_project)
	data = []
	for project in sorted(projects):
		contract_value = flt(contract_by_project.get(project))
		total_cost = flt(cost_by_project.get(project))
		data.append(
			{
				"project": project,
				"project_title": project_titles.get(project, project),
				"contract_value": contract_value,
				"total_cost": total_cost,
				"margin": contract_value - total_cost,
			}
		)
	data.sort(key=lambda row: row["margin"], reverse=True)
	return columns, data
