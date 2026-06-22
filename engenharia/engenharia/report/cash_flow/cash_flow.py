import frappe
from frappe import _
from frappe.utils import add_months, flt, get_first_day, get_last_day, getdate, today

from engenharia.report_visuals import CASH_IN_OUT, bar_chart, currency_summary, month_label
from engenharia.work_costs import FUNDED_BY_OFFICE, office_cash_flow_filters


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = _get_columns()
	data, chart, report_summary = _get_data(filters)
	return columns, data, None, chart, report_summary


def _get_columns():
	return [
		{"fieldname": "date", "label": _("Data"), "fieldtype": "Date", "width": 110},
		{"fieldname": "type", "label": _("Tipo"), "fieldtype": "Data", "width": 100},
		{"fieldname": "description", "label": _("Descrição"), "fieldtype": "Data", "width": 220},
		{
			"fieldname": "inflow",
			"label": _("Entrada"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "outflow",
			"label": _("Saída"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "balance",
			"label": _("Saldo Acumulado"),
			"fieldtype": "Currency",
			"width": 130,
		},
	]


def _get_data(filters):
	months = int(filters.get("months") or 6)
	start = get_first_day(today())
	end = get_last_day(add_months(start, months - 1))
	transactions = []

	for row in frappe.get_all(
		"Payment",
		filters={"status": "Recebido", "received_date": ["between", [start, end]]},
		fields=["name", "description", "received_date", "received_amount", "amount"],
		order_by="received_date asc",
		limit_page_length=10000,
	):
		transactions.append(
			{
				"date": row.received_date,
				"type": _("Entrada"),
				"description": row.description or row.name,
				"inflow": flt(row.received_amount or row.amount),
				"outflow": 0,
			}
		)

	work_cost_payments = frappe.get_all(
		"Work Cost Payment",
		filters={"payment_date": ["between", [start, end]]},
		fields=["parent", "payment_date", "amount"],
		order_by="payment_date asc",
		limit_page_length=10000,
	)
	wc_parent_names = list({row.parent for row in work_cost_payments if row.parent})
	if wc_parent_names:
		wc_parents = frappe.get_all(
			"Work Cost",
			filters={"name": ["in", wc_parent_names]},
			fields=["name", "title", "description", "status", "funded_by"],
			limit_page_length=0,
		)
		wc_lookup = {p.name: p for p in wc_parents}
	else:
		wc_lookup = {}

	for row in work_cost_payments:
		parent = wc_lookup.get(row.parent)
		if not parent or parent.status == "Cancelled" or parent.funded_by != FUNDED_BY_OFFICE:
			continue
		transactions.append(
			{
				"date": row.payment_date,
				"type": _("Saída"),
				"description": parent.title or parent.description or parent.name,
				"inflow": 0,
				"outflow": flt(row.amount),
			}
		)

	reimbursable_payments = frappe.get_all(
		"Reimbursable Expense Payment",
		filters={"payment_date": ["between", [start, end]]},
		fields=["parent", "payment_date", "amount"],
		order_by="payment_date asc",
		limit_page_length=10000,
	)
	re_parent_names = list({row.parent for row in reimbursable_payments if row.parent})
	if re_parent_names:
		re_parents = frappe.get_all(
			"Reimbursable Expense",
			filters={"name": ["in", re_parent_names]},
			fields=["name", "title", "description", "status"],
			limit_page_length=0,
		)
		re_lookup = {p.name: p for p in re_parents}
	else:
		re_lookup = {}

	for row in reimbursable_payments:
		parent = re_lookup.get(row.parent)
		if not parent or parent.status == "Cancelado":
			continue
		transactions.append(
			{
				"date": row.payment_date,
				"type": _("Saída"),
				"description": parent.title or parent.description or parent.name,
				"inflow": 0,
				"outflow": flt(row.amount),
			}
		)

	for row in frappe.get_all(
		"Office Expense",
		filters={
			"status": "Pago",
			"payment_date": ["between", [start, end]],
		},
		fields=["name", "title", "description", "payment_date", "amount"],
		order_by="payment_date asc",
		limit_page_length=10000,
	):
		transactions.append(
			{
				"date": row.payment_date,
				"type": _("Saída"),
				"description": row.title or row.description or row.name,
				"inflow": 0,
				"outflow": flt(row.amount),
			}
		)

	subcontract_payments = frappe.get_all(
		"Subcontract Payment",
		filters={"payment_date": ["between", [start, end]]},
		fields=["parent", "payment_date", "amount"],
		order_by="payment_date asc",
		limit_page_length=10000,
	)
	sc_parent_names = list({row.parent for row in subcontract_payments if row.parent})
	if sc_parent_names:
		sc_parents = frappe.get_all(
			"Subcontract",
			filters={"name": ["in", sc_parent_names]},
			fields=["name", "title", "description", "status", "funded_by"],
			limit_page_length=0,
		)
		sc_lookup = {p.name: p for p in sc_parents}
	else:
		sc_lookup = {}

	for row in subcontract_payments:
		parent = sc_lookup.get(row.parent)
		if not parent or parent.status == "Cancelled" or parent.funded_by != FUNDED_BY_OFFICE:
			continue
		transactions.append(
			{
				"date": row.payment_date,
				"type": _("Saída"),
				"description": parent.title or parent.description or parent.name,
				"inflow": 0,
				"outflow": flt(row.amount),
			}
		)

	transactions.sort(key=lambda item: getdate(item["date"]))

	total_inflow = 0.0
	total_outflow = 0.0
	balance = 0.0
	data = []

	for row in transactions:
		total_inflow += flt(row["inflow"])
		total_outflow += flt(row["outflow"])
		balance += flt(row["inflow"]) - flt(row["outflow"])
		row["balance"] = balance
		data.append(row)

	net = total_inflow - total_outflow

	if data:
		data.append({})
		data.append(
			{
				"date": None,
				"type": "",
				"description": _("Total Entradas"),
				"inflow": total_inflow,
				"outflow": 0,
				"balance": None,
			}
		)
		data.append(
			{
				"date": None,
				"type": "",
				"description": _("Total Saídas"),
				"inflow": 0,
				"outflow": total_outflow,
				"balance": None,
			}
		)
		data.append(
			{
				"date": None,
				"type": "",
				"description": _("Saldo Líquido do Período"),
				"inflow": 0,
				"outflow": 0,
				"balance": net,
			}
		)

	chart = _build_monthly_chart(transactions, start, months)
	report_summary = [
		currency_summary(total_inflow, _("Total Entradas"), "Green"),
		currency_summary(total_outflow, _("Total Saídas"), "Red"),
		currency_summary(net, _("Saldo Líquido"), "Green" if net >= 0 else "Red"),
	]
	return data, chart, report_summary


def _build_monthly_chart(transactions, period_start, months):
	month_totals = {}
	for i in range(months):
		month_start = get_first_day(add_months(period_start, i))
		label = month_label(month_start)
		month_totals[label] = {"inflow": 0.0, "outflow": 0.0}

	for row in transactions:
		label = month_label(row["date"])
		if label not in month_totals:
			month_totals[label] = {"inflow": 0.0, "outflow": 0.0}
		month_totals[label]["inflow"] += flt(row.get("inflow"))
		month_totals[label]["outflow"] += flt(row.get("outflow"))

	if not transactions:
		return None

	labels = list(month_totals.keys())
	return bar_chart(
		labels,
		[
			{"name": _("Entradas"), "values": [month_totals[l]["inflow"] for l in labels]},
			{"name": _("Saídas"), "values": [month_totals[l]["outflow"] for l in labels]},
		],
		CASH_IN_OUT,
	)
