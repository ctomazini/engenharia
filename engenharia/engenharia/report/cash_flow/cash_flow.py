import frappe
from frappe import _
from frappe.utils import add_months, flt, get_first_day, get_last_day, getdate, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"fieldname": "date", "label": _("Data"), "fieldtype": "Date", "width": 110},
		{"fieldname": "type", "label": _("Tipo"), "fieldtype": "Data", "width": 100},
		{"fieldname": "description", "label": _("Descrição"), "fieldtype": "Data", "width": 220},
		{"fieldname": "inflow", "label": _("Entrada"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "outflow", "label": _("Saída"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "balance", "label": _("Saldo"), "fieldtype": "Currency", "width": 120},
	]
	months = int(filters.get("months") or 6)
	start = get_first_day(today())
	end = get_last_day(add_months(start, months - 1))
	transactions = []

	for row in frappe.get_all(
		"Payment",
		filters={"status": "Recebido", "received_date": ["between", [start, end]]},
		fields=["name", "description", "received_date", "received_amount", "amount"],
		order_by="received_date asc",
		limit=0,
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

	for row in frappe.get_all(
		"Work Cost",
		filters={"status": "Pago", "date": ["between", [start, end]]},
		fields=["name", "description", "date", "amount"],
		order_by="date asc",
		limit=0,
	):
		transactions.append(
			{
				"date": row.date,
				"type": _("Saída"),
				"description": row.description or row.name,
				"inflow": 0,
				"outflow": flt(row.amount),
			}
		)

	for row in frappe.get_all(
		"Subcontract Payment",
		filters={"payment_date": ["between", [start, end]]},
		fields=["parent", "payment_date", "amount"],
		order_by="payment_date asc",
		limit=0,
	):
		parent = frappe.db.get_value(
			"Subcontract",
			row.parent,
			["name", "title", "description", "status"],
			as_dict=True,
		)
		if not parent or parent.status == "Cancelled":
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
		"Reimbursable Expense",
		filters={
			"status": ["!=", "Cancelado"],
			"payment_date": ["between", [start, end]],
		},
		fields=["name", "description", "payment_date", "amount"],
		order_by="payment_date asc",
		limit=0,
	):
		transactions.append(
			{
				"date": row.payment_date,
				"type": _("Saída"),
				"description": row.description or row.name,
				"inflow": 0,
				"outflow": flt(row.amount),
			}
		)

	transactions.sort(key=lambda item: getdate(item["date"]))
	balance = 0
	data = []
	for row in transactions:
		balance += flt(row["inflow"]) - flt(row["outflow"])
		row["balance"] = balance
		data.append(row)
	return columns, data
