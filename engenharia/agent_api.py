"""APIs whitelisted de leitura agregada para agentes IA."""

import frappe
from frappe import _
from frappe.utils import add_months, flt, getdate, today

from engenharia.dashboard._helpers import user_is_engenharia_manager
from engenharia.titles import get_customer_name
from engenharia.work_costs import get_combined_project_cost, get_work_cost_totals_by_category

_FINANCIAL_SUMMARY_KEYS = (
	"contract_value",
	"contract_status",
	"amount_receivable",
	"pending_payments_count",
	"amount_reimbursable",
	"total_costs",
	"margin",
)

ACTIVE_PROJECT_STATUSES = ("Orçamento", "Em andamento", "Paralisada")


@frappe.whitelist()
def get_active_projects() -> list[dict]:
	frappe.has_permission("Construction Project", "read", throw=True)

	rows = frappe.get_all(
		"Construction Project",
		filters={"status": ["in", list(ACTIVE_PROJECT_STATUSES)]},
		fields=["name", "title", "customer", "city", "status", "project_type"],
		order_by="modified desc",
		limit=100,
	)
	customer_names = {
		c.name: c.customer_name
		for c in frappe.get_all(
			"Customer",
			filters={"name": ["in", [r.customer for r in rows if r.customer]]},
			fields=["name", "customer_name"],
			limit=100,
		)
	}
	for row in rows:
		row["customer_name"] = customer_names.get(row.customer) or get_customer_name(row.customer)
	return rows


@frappe.whitelist()
def get_project_summary(project: str) -> dict:
	frappe.has_permission("Construction Project", "read", doc=project, throw=True)

	doc = frappe.get_doc("Construction Project", project)
	contract = frappe.get_all(
		"Engineering Contract",
		filters={"project": project, "status": ["!=", "Cancelado"]},
		fields=["name", "current_value", "status"],
		order_by="modified desc",
		limit=1,
	)
	payments = frappe.get_all(
		"Payment",
		filters={"project": project, "status": ["in", ["Pendente", "Vencido"]]},
		fields=["amount"],
		limit=100,
	)
	reimbursable = frappe.get_all(
		"Reimbursable Expense",
		filters={"project": project, "status": "A reembolsar"},
		fields=["amount"],
		limit=100,
	)
	total_costs = get_combined_project_cost(project)
	deadlines = frappe.get_all(
		"Deadline",
		filters={"project": project, "status": "Pendente", "due_date": [">=", today()]},
		fields=["name", "description", "due_date"],
		order_by="due_date asc",
		limit=20,
	)

	contract_value = flt(contract[0].current_value) if contract else 0

	data = {
		"project": doc.name,
		"title": doc.title or doc.name,
		"customer": doc.customer,
		"customer_name": get_customer_name(doc.customer),
		"city": doc.city,
		"status": doc.status,
		"project_type": doc.project_type,
		"contract_value": contract_value,
		"contract_status": contract[0].status if contract else None,
		"amount_receivable": sum(flt(row.amount) for row in payments),
		"pending_payments_count": len(payments),
		"amount_reimbursable": sum(flt(row.amount) for row in reimbursable),
		"total_costs": total_costs,
		"margin": contract_value - total_costs,
		"upcoming_deadlines": deadlines,
	}

	if not user_is_engenharia_manager():
		for key in _FINANCIAL_SUMMARY_KEYS:
			data.pop(key, None)
		data["financial_restricted"] = True

	return data


@frappe.whitelist()
def get_financial_overview() -> dict:
	"""Aggregated financial data — Engenharia Manager only."""
	if not user_is_engenharia_manager():
		frappe.throw(_("Sem permissão"), frappe.PermissionError)
	frappe.has_permission("Payment", "read", throw=True)

	hoje = getdate(today())
	mes_inicio = hoje.replace(day=1)
	mes_fim = add_months(mes_inicio, 1)

	overview = {
		"overdue": frappe.db.count("Payment", {"status": "Vencido"}),
		"pending": frappe.db.count("Payment", {"status": "Pendente"}),
		"received_this_month": frappe.db.count(
			"Payment",
			{"status": "Recebido", "received_date": ["between", [mes_inicio, mes_fim]]},
		),
	}

	overdue_val = frappe.db.sql(
		"SELECT COALESCE(SUM(amount), 0) FROM `tabPayment` WHERE status = 'Vencido'",
		as_list=True,
	)
	overview["overdue_amount"] = flt(overdue_val[0][0]) if overdue_val else 0

	received_val = frappe.db.sql(
		"""SELECT COALESCE(SUM(received_amount), 0) FROM `tabPayment`
		WHERE status = 'Recebido' AND received_date BETWEEN %s AND %s""",
		(mes_inicio, mes_fim),
		as_list=True,
	)
	overview["received_amount"] = flt(received_val[0][0]) if received_val else 0

	return overview


@frappe.whitelist()
def get_costs_by_category(project: str) -> dict:
	frappe.has_permission("Construction Project", "read", doc=project, throw=True)
	if not user_is_engenharia_manager():
		frappe.throw(_("Sem permissão"), frappe.PermissionError)
	frappe.has_permission("Work Cost", "read", throw=True)

	totals = get_work_cost_totals_by_category(project=project)
	category_names = {
		c.name: c.category_name
		for c in frappe.get_all("Cost Category", fields=["name", "category_name"], limit=200)
	}
	rows = []
	for key, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True):
		rows.append(
			{
				"cost_category": None if key == "Sem classificação" else key,
				"category_name": category_names.get(key, key),
				"amount": amount,
			}
		)
	return {
		"project": project,
		"categories": rows,
		"total": sum(flt(row["amount"]) for row in rows),
	}
