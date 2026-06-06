import frappe
from frappe.utils import add_days, flt, get_first_day, get_last_day, today

from engenharia.dashboard._helpers import LIST_LIMIT_MAX
from engenharia.work_costs import (
	get_firm_month_outflows,
	office_cash_flow_filters,
	office_subcontract_filters,
)


def _sum_amount(rows, field="amount"):
	return sum(flt(getattr(r, field, 0)) for r in rows)


def build_kpis(hoje, period_end, month_start, month_end, include_financial=True):
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
	overdue_deadlines = frappe.db.count("Deadline", {"status": "Pendente", "due_date": ["<", hoje]})
	open_tasks = frappe.db.count("Task", {"status": ["in", ["A fazer", "Fazendo"]]})
	late_tasks = frappe.db.count(
		"Task",
		{
			"status": ["in", ["A fazer", "Fazendo"]],
			"due_date": ["<", hoje],
		},
	)
	permits_today = frappe.db.count(
		"Permit",
		{"protocol_date": hoje, "status": ["not in", ["Cancelado"]]},
	)
	permits_tomorrow = frappe.db.count(
		"Permit",
		{"protocol_date": add_days(hoje, 1), "status": ["not in", ["Cancelado"]]},
	)

	result = {
		"active_projects": active_projects,
		"urgent_deadlines": urgent_deadlines,
		"overdue_deadlines": overdue_deadlines,
		"open_tasks": open_tasks,
		"late_tasks": late_tasks,
		"permits_today": permits_today,
		"permits_tomorrow": permits_tomorrow,
		"total_customers": frappe.db.count("Customer"),
	}

	if not include_financial:
		return result

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
	period_pending = frappe.get_all(
		"Payment",
		filters={
			"status": "Pendente",
			"due_date": ["between", [hoje, period_end]],
		},
		fields=["amount"],
		limit=LIST_LIMIT_MAX,
	)
	received_month = frappe.get_all(
		"Payment",
		filters={
			"status": "Recebido",
			"received_date": ["between", [month_start, month_end]],
		},
		fields=["received_amount", "amount"],
		limit=LIST_LIMIT_MAX,
	)
	received_period = frappe.get_all(
		"Payment",
		filters={
			"status": "Recebido",
			"received_date": ["between", [hoje, period_end]],
		},
		fields=["received_amount", "amount"],
		limit=LIST_LIMIT_MAX,
	)
	reimbursable = frappe.get_all(
		"Reimbursable Expense",
		filters={"status": "A reembolsar"},
		fields=["amount"],
		limit=LIST_LIMIT_MAX,
	)
	firm_month_outflows = get_firm_month_outflows(month_start, month_end)
	pending_work_cost_rows = frappe.get_all(
		"Work Cost",
		filters=office_cash_flow_filters({"status": "Pendente"}),
		fields=["amount"],
		limit=LIST_LIMIT_MAX,
	)
	pending_subcontract_rows = frappe.get_all(
		"Subcontract",
		filters=office_subcontract_filters({"status": ["in", ["Open", "Partially Paid"]]}),
		fields=["outstanding"],
		limit=LIST_LIMIT_MAX,
	)

	receivable_amount = _sum_amount(pending_payments) + _sum_amount(overdue_payments)
	overdue_amount = _sum_amount(overdue_payments)
	received_month_amount = sum(flt(r.received_amount or r.amount) for r in received_month)
	received_period_amount = sum(flt(r.received_amount or r.amount) for r in received_period)
	period_pending_amount = _sum_amount(period_pending)
	base_taxa = overdue_amount + received_month_amount + period_pending_amount
	taxa_recebimento = round((received_month_amount / base_taxa) * 100, 1) if base_taxa else 100

	active_contracts = frappe.db.count("Engineering Contract", {"status": "Vigente"})
	spec_total_rows = frappe.get_all(
		"Project Item",
		fields=["total_value"],
		limit=LIST_LIMIT_MAX,
	)
	spec_project_total = sum(flt(r.total_value) for r in spec_total_rows)

	result.update(
		{
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
				"count": firm_month_outflows["count"],
				"amount": firm_month_outflows["amount"],
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
			"pending_work_costs": {
				"count": len(pending_work_cost_rows),
				"amount": _sum_amount(pending_work_cost_rows),
			},
			"spec_project_total": spec_project_total,
		}
	)
	return result


def build_summary(hoje, kpis, period_days):
	overdue_count = (kpis.get("amount_overdue") or {}).get("count") or 0
	return {
		"date_label": frappe.utils.formatdate(hoje, "EEEE, d 'de' MMMM"),
		"period_days": period_days,
		"urgency": "high" if overdue_count or kpis.get("urgent_deadlines") else "normal",
	}
