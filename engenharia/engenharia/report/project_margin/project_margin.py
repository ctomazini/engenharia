import frappe
from frappe import _
from frappe.utils import flt

from engenharia.work_costs import FUNDED_BY_OFFICE, get_subcontract_paid_totals_by_project


def execute(filters=None):
	columns = [
		{
			"fieldname": "project",
			"label": _("Obra"),
			"fieldtype": "Link",
			"options": "Construction Project",
			"width": 180,
		},
		{"fieldname": "project_title", "label": _("Título"), "fieldtype": "Data", "width": 220},
		{
			"fieldname": "contract_value",
			"label": _("Valor Contratado"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "received_revenue",
			"label": _("Receita Recebida"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "total_cost",
			"label": _("Custos de Obra"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "reimbursable_expense",
			"label": _("Despesas Reembolsáveis"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "contractual_margin",
			"label": _("Margem Contratual"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "realized_margin",
			"label": _("Margem Realizada"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "received_percent",
			"label": _("% Recebido"),
			"fieldtype": "Percent",
			"width": 90,
		},
	]

	contract_by_project = {}
	for row in frappe.get_all(
		"Engineering Contract",
		filters={"status": ["in", ["Vigente", "Quitado"]]},
		fields=["project", "current_value"],
		limit=0,
	):
		contract_by_project[row.project] = contract_by_project.get(row.project, 0) + flt(row.current_value)

	received_by_project = {}
	for row in frappe.get_all(
		"Payment",
		filters={"status": "Recebido"},
		fields=["project", "received_amount", "amount"],
		limit=0,
	):
		if not row.project:
			continue
		received_by_project[row.project] = received_by_project.get(row.project, 0) + flt(
			row.received_amount or row.amount
		)

	cost_by_project = {}
	firm_cost_by_project = {}
	for row in frappe.get_all(
		"Work Cost",
		filters={"status": "Pago"},
		fields=["project", "amount", "funded_by"],
		limit=0,
	):
		if not row.project:
			continue
		cost_by_project[row.project] = cost_by_project.get(row.project, 0) + flt(row.amount)
		if row.funded_by == FUNDED_BY_OFFICE:
			firm_cost_by_project[row.project] = firm_cost_by_project.get(row.project, 0) + flt(row.amount)

	for project, paid in get_subcontract_paid_totals_by_project(office_funded_only=False).items():
		cost_by_project[project] = cost_by_project.get(project, 0) + flt(paid)

	for project, paid in get_subcontract_paid_totals_by_project(office_funded_only=True).items():
		firm_cost_by_project[project] = firm_cost_by_project.get(project, 0) + flt(paid)

	reimbursable_by_project = {}
	for row in frappe.get_all(
		"Reimbursable Expense",
		filters={"status": ["!=", "Cancelado"]},
		fields=["project", "amount"],
		limit=0,
	):
		reimbursable_by_project[row.project] = reimbursable_by_project.get(row.project, 0) + flt(row.amount)

	project_titles = {
		p.name: p.title
		for p in frappe.get_all("Construction Project", fields=["name", "title"], limit=0)
	}
	projects = (
		set(contract_by_project)
		| set(received_by_project)
		| set(cost_by_project)
		| set(reimbursable_by_project)
	)
	data = []
	for project in sorted(projects):
		contract_value = flt(contract_by_project.get(project))
		received_revenue = flt(received_by_project.get(project))
		total_cost = flt(cost_by_project.get(project))
		firm_cost = flt(firm_cost_by_project.get(project))
		reimbursable_expense = flt(reimbursable_by_project.get(project))
		contractual_margin = contract_value - total_cost
		realized_margin = received_revenue - firm_cost - reimbursable_expense
		received_percent = (received_revenue / contract_value * 100) if contract_value else 0
		data.append(
			{
				"project": project,
				"project_title": project_titles.get(project, project),
				"contract_value": contract_value,
				"received_revenue": received_revenue,
				"total_cost": total_cost,
				"reimbursable_expense": reimbursable_expense,
				"contractual_margin": contractual_margin,
				"realized_margin": realized_margin,
				"received_percent": round(received_percent, 1),
			}
		)
	data.sort(key=lambda row: row["realized_margin"], reverse=True)
	return columns, data
