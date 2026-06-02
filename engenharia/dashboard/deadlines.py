import frappe
from frappe.utils import add_days, date_diff

from engenharia.dashboard._helpers import (
	LIST_LIMIT_MAX,
	_customer_name_lookup,
	_project_lookup,
)


def build_alerts(hoje, period_end):
	alertas = []
	rows = frappe.get_all(
		"Deadline",
		filters={
			"status": "Pendente",
			"due_date": ["between", [hoje, add_days(hoje, 1)]],
		},
		fields=["name", "description", "due_date", "customer", "project", "priority"],
		order_by="due_date asc",
		limit=20,
	)
	customer_map = _customer_name_lookup([r.customer for r in rows if r.customer])
	for row in rows:
		dias = date_diff(row.due_date, hoje)
		alertas.append(
			{
				"type": "deadline",
				"level": "red" if dias <= 0 else "yellow",
				"title": row.description or row.name,
				"date": row.due_date,
				"customer_name": customer_map.get(row.customer, row.customer or ""),
				"doctype": "Deadline",
				"docname": row.name,
			}
		)

	expiring_permits = frappe.get_all(
		"Permit",
		filters={
			"status": ["in", ["Pendente", "Em análise", "Aprovado"]],
			"expiry_date": ["between", [hoje, period_end]],
		},
		fields=["name", "permit_type", "expiry_date", "project", "customer"],
		order_by="expiry_date asc",
		limit=20,
	)
	project_map = _project_lookup([p.project for p in expiring_permits if p.project])
	for row in expiring_permits:
		alertas.append(
			{
				"type": "permit",
				"level": "orange",
				"title": row.permit_type or row.name,
				"date": row.expiry_date,
				"customer_name": (project_map.get(row.project) or {}).get("title") or row.project or "",
				"doctype": "Permit",
				"docname": row.name,
			}
		)
	return alertas


def get_deadlines(hoje, period_end, limit):
	rows = frappe.get_all(
		"Deadline",
		filters={"due_date": ["between", [hoje, period_end]]},
		fields=["name", "description", "due_date", "customer", "project", "status", "priority"],
		order_by="due_date asc",
		limit=limit,
	)
	customer_map = _customer_name_lookup([r.customer for r in rows if r.customer])
	for row in rows:
		row["customer_name"] = customer_map.get(row.customer, row.customer or "")
		row["days_remaining"] = date_diff(row.due_date, hoje) if row.due_date else None
	return rows
