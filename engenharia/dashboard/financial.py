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
		limit_page_length=LIST_LIMIT_MAX,
	)
	project_map = _project_lookup([p.project for p in pending if p.project])
	customer_map = _customer_name_lookup(
		[p.customer for p in pending if p.customer]
		+ [project_map[p.project].customer for p in pending if p.project and project_map.get(p.project)]
	)

	for row in pending:
		row["project_title"] = (project_map.get(row.project) or {}).get("title") or row.project or ""
		row["customer_name"] = customer_map.get(row.customer, row.customer or "")
		row["valor_total"] = flt(row.amount)
		row["vencimento"] = row.due_date
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
	received_month = flt(kpis["received_month"]["amount"])
	previsto = kpis.get("previsto_periodo") or {"count": 0, "valor": 0}
	previsto_valor = flt(previsto.get("valor"))
	base_inadimplencia = overdue + received_month + previsto_valor
	taxa_inadimplencia = round((overdue / base_inadimplencia) * 100, 1) if base_inadimplencia else 0
	saidas = reimbursable + costs

	grafico = [
		{"label": _("A reembolsar"), "valor": reimbursable, "tone": "neutral"},
		{"label": _("Custos do mês"), "valor": costs, "tone": "info"},
	]

	return {
		"pending_payments": pending,
		"chart": grafico,
		"grafico": grafico,
		"fluxo": {
			"entrada": {
				"label": _("A receber (total)"),
				"amount": receivable,
				"tone": "warning",
			},
			"saida": {
				"label": _("Saídas (reembolsar + custos)"),
				"amount": saidas,
				"tone": "info",
			},
		},
		"recebido_mes": kpis["received_month"],
		"vencido": kpis["parcelas_vencidas"],
		"previsto_periodo": previsto,
		"previsto_semana": previsto,
		"taxa_recebimento": kpis.get("taxa_recebimento") or 0,
		"taxa_inadimplencia": taxa_inadimplencia,
	}


def get_pending_reimbursables(limit):
	rows = frappe.get_all(
		"Reimbursable Expense",
		filters={"status": "A reembolsar"},
		fields=["name", "title", "project", "customer", "amount", "payment_date", "status"],
		order_by="payment_date asc",
		limit_page_length=limit,
	)
	project_map = _project_lookup([r.project for r in rows if r.project])
	customer_map = _customer_name_lookup([r.customer for r in rows if r.customer])
	for row in rows:
		row["project_title"] = (project_map.get(row.project) or {}).get("title") or row.project or ""
		row["customer_name"] = customer_map.get(row.customer, row.customer or "")
		row["valor"] = flt(row.amount)
		row["data"] = row.payment_date
	return rows


def get_total_reimbursables_month(month_start, month_end):
	rows = frappe.get_all(
		"Reimbursable Expense",
		filters={
			"status": ["!=", "Cancelado"],
			"payment_date": ["between", [month_start, month_end]],
		},
		fields=["amount"],
		limit_page_length=LIST_LIMIT_MAX,
	)
	return sum(flt(r.amount) for r in rows)


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
