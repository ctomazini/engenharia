import frappe
from frappe.utils import add_days, flt, get_first_day, get_last_day, today

from engenharia.dashboard._helpers import LIST_LIMIT_MAX


def _sum_amount(rows, field="amount"):
	return sum(flt(getattr(r, field, 0)) for r in rows)


def build_kpis(hoje, period_end, month_start, month_end):
	pending_payments = frappe.get_all(
		"Payment",
		filters={"status": "Pendente"},
		fields=["amount"],
		limit_page_length=LIST_LIMIT_MAX,
	)
	overdue_payments = frappe.get_all(
		"Payment",
		filters={"status": "Vencido"},
		fields=["amount"],
		limit_page_length=LIST_LIMIT_MAX,
	)
	period_pending = frappe.get_all(
		"Payment",
		filters={
			"status": "Pendente",
			"due_date": ["between", [hoje, period_end]],
		},
		fields=["amount"],
		limit_page_length=LIST_LIMIT_MAX,
	)
	received_month = frappe.get_all(
		"Payment",
		filters={
			"status": "Recebido",
			"received_date": ["between", [month_start, month_end]],
		},
		fields=["received_amount", "amount"],
		limit_page_length=LIST_LIMIT_MAX,
	)
	received_period = frappe.get_all(
		"Payment",
		filters={
			"status": "Recebido",
			"received_date": ["between", [hoje, period_end]],
		},
		fields=["received_amount", "amount"],
		limit_page_length=LIST_LIMIT_MAX,
	)
	reimbursable = frappe.get_all(
		"Reimbursable Expense",
		filters={"status": "A reembolsar"},
		fields=["amount"],
		limit_page_length=LIST_LIMIT_MAX,
	)
	month_costs = frappe.get_all(
		"Work Cost",
		filters={
			"status": ["!=", "Cancelado"],
			"date": ["between", [month_start, month_end]],
		},
		fields=["amount"],
		limit_page_length=LIST_LIMIT_MAX,
	)

	active_projects = frappe.db.count(
		"Construction Project", {"status": ["in", ["Orçamento", "Em andamento"]]}
	)
	active_contracts = frappe.db.count("Engineering Contract", {"status": "Vigente"})
	urgent_deadlines = frappe.db.count(
		"Deadline",
		{
			"status": "Pendente",
			"due_date": ["between", [hoje, add_days(hoje, 3)]],
		},
	)
	overdue_deadlines = frappe.db.count("Deadline", {"status": "Pendente", "due_date": ["<", hoje]})
	open_tasks = frappe.db.count("Task", {"status": ["in", ["A fazer", "Fazendo"]]})
	late_tasks = frappe.db.count(
		"Task",
		{
			"status": ["in", ["A fazer", "Fazendo"]],
			"due_date": ["<", hoje],
		},
	)

	receivable_amount = _sum_amount(pending_payments) + _sum_amount(overdue_payments)
	overdue_amount = _sum_amount(overdue_payments)
	received_month_amount = sum(flt(r.received_amount or r.amount) for r in received_month)
	received_period_amount = sum(flt(r.received_amount or r.amount) for r in received_period)
	period_pending_amount = _sum_amount(period_pending)
	base_taxa = overdue_amount + received_month_amount + period_pending_amount
	taxa_recebimento = round((received_month_amount / base_taxa) * 100, 1) if base_taxa else 100

	spec_total_rows = frappe.get_all(
		"Project Item",
		fields=["total_value"],
		limit_page_length=LIST_LIMIT_MAX,
	)
	spec_project_total = sum(flt(r.total_value) for r in spec_total_rows)

	return {
		"active_projects": active_projects,
		"active_contracts": active_contracts,
		"amount_receivable": {
			"count": len(pending_payments) + len(overdue_payments),
			"amount": receivable_amount,
		},
		"amount_overdue": {
			"count": len(overdue_payments),
			"amount": overdue_amount,
		},
		"amount_reimbursable": {
			"count": len(reimbursable),
			"amount": _sum_amount(reimbursable),
		},
		"month_costs": {
			"count": len(month_costs),
			"amount": _sum_amount(month_costs),
		},
		"received_month": {
			"count": len(received_month),
			"amount": received_month_amount,
		},
		"received_period": {
			"count": len(received_period),
			"amount": received_period_amount,
		},
		"parcelas_vencidas": {
			"count": len(overdue_payments),
			"valor": overdue_amount,
		},
		"previsto_periodo": {
			"count": len(period_pending),
			"valor": period_pending_amount,
		},
		"taxa_recebimento": taxa_recebimento,
		"urgent_deadlines": urgent_deadlines,
		"overdue_deadlines": overdue_deadlines,
		"open_tasks": open_tasks,
		"late_tasks": late_tasks,
		"total_customers": frappe.db.count("Customer"),
		"spec_project_total": spec_project_total,
	}


def build_summary(hoje, kpis, period_days):
	return {
		"date_label": frappe.utils.formatdate(hoje, "EEEE, d 'de' MMMM"),
		"period_days": period_days,
		"urgency": "high" if kpis["amount_overdue"]["count"] or kpis["urgent_deadlines"] else "normal",
	}
