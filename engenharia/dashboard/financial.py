import frappe
from frappe import _
from frappe.utils import date_diff, flt, today

from engenharia.dashboard._helpers import (
	LIST_LIMIT_MAX,
	_customer_name_lookup,
	_project_lookup,
)


def build_financial(hoje, period_end, kpis):
	pending = frappe.get_all(
		"Payment",
		filters={
			"status": ["in", ["Pendente", "Vencido"]],
			"due_date": ["between", [hoje, period_end]],
		},
		fields=[
			"name",
			"title",
			"project",
			"customer",
			"amount",
			"due_date",
			"status",
		],
		order_by="due_date asc",
		limit=LIST_LIMIT_MAX,
	)
	project_map = _project_lookup([p.project for p in pending if p.project])
	customer_map = _customer_name_lookup(
		[p.customer for p in pending if p.customer]
		+ [project_map[p.project].customer for p in pending if p.project and project_map.get(p.project)]
	)

	for row in pending:
		row["project_title"] = (project_map.get(row.project) or {}).get("title") or row.project or ""
		row["customer_name"] = customer_map.get(row.customer, row.customer or "")
		if row.due_date:
			row["days_overdue"] = max(date_diff(hoje, row.due_date), 0) if row.status == "Vencido" else 0
			row["days_until_due"] = max(date_diff(row.due_date, hoje), 0)
		else:
			row["days_overdue"] = 0
			row["days_until_due"] = 0

	receivable = flt(kpis["amount_receivable"]["amount"])
	overdue = flt(kpis["amount_overdue"]["amount"])
	reimbursable = flt(kpis["amount_reimbursable"]["amount"])
	costs = flt(kpis["month_costs"]["amount"])

	return {
		"pending_payments": pending,
		"chart": [
			{"label": "A receber", "amount": receivable, "tone": "warning"},
			{"label": "Vencido", "amount": overdue, "tone": "danger"},
			{"label": "A reembolsar", "amount": reimbursable, "tone": "neutral"},
			{"label": "Custos do mês", "amount": costs, "tone": "info"},
		],
	}


def mark_payment_received(payment_name, received_date=None):
	frappe.has_permission("Payment", "write", throw=True)
	doc = frappe.get_doc("Payment", payment_name)
	if doc.status == "Recebido":
		frappe.throw(_("Pagamento já está recebido."))
	doc.status = "Recebido"
	doc.received_amount = doc.amount
	doc.received_date = received_date or today()
	doc.save()
	return {"name": doc.name, "status": doc.status}
