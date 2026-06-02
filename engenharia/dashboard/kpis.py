import frappe
from frappe.utils import add_days, flt, get_first_day, get_last_day, today

from engenharia.dashboard._helpers import LIST_LIMIT_MAX


def build_kpis(hoje, period_end, month_start, month_end):
	pending_payments = frappe.get_all(
		"Payment",
		filters={"status": "Pendente"},
		fields=["amount"],
		limit=LIST_LIMIT_MAX,
	)
	overdue_payments = frappe.get_all(
		"Payment",
		filters={"status": "Vencido"},
		fields=["amount"],
		limit=LIST_LIMIT_MAX,
	)
	reimbursable = frappe.get_all(
		"Reimbursable Expense",
		filters={"status": "A reembolsar"},
		fields=["amount"],
		limit=LIST_LIMIT_MAX,
	)
	month_costs = frappe.get_all(
		"Work Cost",
		filters={
			"status": ["!=", "Cancelado"],
			"date": ["between", [month_start, month_end]],
		},
		fields=["amount"],
		limit=LIST_LIMIT_MAX,
	)

	active_projects = frappe.db.count(
		"Construction Project", {"status": ["in", ["Orçamento", "Em andamento"]]}
	)
	urgent_deadlines = frappe.db.count(
		"Deadline",
		{
			"status": "Pendente",
			"due_date": ["between", [hoje, add_days(hoje, 3)]],
		},
	)
	open_tasks = frappe.db.count("Task", {"status": ["in", ["A fazer", "Fazendo"]]})

	return {
		"active_projects": active_projects,
		"amount_receivable": {
			"count": len(pending_payments) + len(overdue_payments),
			"amount": sum(flt(p.amount) for p in pending_payments)
			+ sum(flt(p.amount) for p in overdue_payments),
		},
		"amount_overdue": {
			"count": len(overdue_payments),
			"amount": sum(flt(p.amount) for p in overdue_payments),
		},
		"amount_reimbursable": {
			"count": len(reimbursable),
			"amount": sum(flt(r.amount) for r in reimbursable),
		},
		"month_costs": {
			"count": len(month_costs),
			"amount": sum(flt(c.amount) for c in month_costs),
		},
		"urgent_deadlines": urgent_deadlines,
		"open_tasks": open_tasks,
		"total_customers": frappe.db.count("Customer"),
	}


def build_summary(hoje, kpis, period_days):
	return {
		"date_label": frappe.utils.formatdate(hoje, "EEEE, d 'de' MMMM"),
		"period_days": period_days,
		"urgency": "high"
		if kpis["amount_overdue"]["count"] or kpis["urgent_deadlines"]
		else "normal",
	}
