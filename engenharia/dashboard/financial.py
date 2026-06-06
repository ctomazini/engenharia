import frappe
from frappe import _
from frappe.utils import date_diff, flt, formatdate, get_first_day, get_last_day, today

from engenharia.dashboard._helpers import (
	LIST_LIMIT_MAX,
	_customer_name_lookup,
	_project_lookup,
)
from engenharia.work_costs import (
	get_subcontract_payments_by_category_month,
	office_cash_flow_filters,
)

_CHART_TONES = ("info", "warning", "danger", "success", "neutral")


def _build_cost_composition_chart(month_start, month_end):
	rows = frappe.get_all(
		"Work Cost",
		filters=office_cash_flow_filters(
			{
				"status": ["!=", "Cancelado"],
				"date": ["between", [month_start, month_end]],
			}
		),
		fields=["cost_category", "amount"],
		limit=LIST_LIMIT_MAX,
	)
	totals: dict[str, float] = {}
	for row in rows:
		key = row.cost_category or _("Sem categoria")
		totals[key] = totals.get(key, 0) + flt(row.amount)

	for key, amount in get_subcontract_payments_by_category_month(month_start, month_end).items():
		totals[key] = totals.get(key, 0) + flt(amount)

	if not totals:
		return []

	category_names = {
		category.name: category.category_name
		for category in frappe.get_all("Cost Category", fields=["name", "category_name"], limit=LIST_LIMIT_MAX)
	}
	grafico = []
	for index, (key, amount) in enumerate(sorted(totals.items(), key=lambda item: item[1], reverse=True)):
		if amount <= 0:
			continue
		label = category_names.get(key, key)
		grafico.append(
			{
				"label": label,
				"valor": amount,
				"tone": _CHART_TONES[index % len(_CHART_TONES)],
			}
		)
	return grafico


def build_financial(hoje, period_end, kpis, month_start=None, month_end=None):
	month_start = month_start or get_first_day(hoje)
	month_end = month_end or get_last_day(hoje)

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
		row["valor_total"] = flt(row.amount)
		row["vencimento"] = row.due_date
		if row.due_date:
			row["days_overdue"] = max(date_diff(hoje, row.due_date), 0) if row.status == "Vencido" else 0
			row["days_until_due"] = max(date_diff(row.due_date, hoje), 0)
		else:
			row["days_overdue"] = 0
			row["days_until_due"] = 0

	overdue = flt(kpis["amount_overdue"]["amount"])
	received_month = flt(kpis["received_month"]["amount"])
	month_costs = flt(kpis["month_costs"]["amount"])
	previsto = kpis.get("previsto_periodo") or {"count": 0, "valor": 0}
	previsto_valor = flt(previsto.get("valor"))
	base_inadimplencia = overdue + received_month + previsto_valor
	taxa_inadimplencia = round((overdue / base_inadimplencia) * 100, 1) if base_inadimplencia else 0

	grafico = _build_cost_composition_chart(month_start, month_end)
	month_label = formatdate(month_start, "MMMM yyyy")

	return {
		"pending_payments": pending,
		"chart": grafico,
		"grafico": grafico,
		"fluxo": {
			"month_label": month_label,
			"fixed_to_month": True,
			"entrada": {
				"label": _("Entradas do mês"),
				"amount": received_month,
				"detail": _("recebimentos confirmados no mês"),
				"tone": "success",
			},
			"saida": {
				"label": _("Saídas do mês"),
				"amount": month_costs,
				"detail": _("custos de obra e subcontratos pagos pelo escritório no mês"),
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
		limit=limit,
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
		limit=LIST_LIMIT_MAX,
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
