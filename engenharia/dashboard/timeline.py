import frappe
from frappe.utils import add_days, date_diff, flt, get_first_day, get_last_day, today

from engenharia.dashboard._helpers import (
	LIST_LIMIT_MAX,
	_customer_name_lookup,
	_project_lookup,
)


def build_timeline(hoje, period_end, deadlines, tasks):
	items = []
	for row in deadlines or []:
		dias = row.get("days_remaining", 99)
		items.append(
			{
				"type": "deadline",
				"sort_key": f"{row.get('due_date') or hoje} 12:00:00",
				"date": row.get("due_date"),
				"title": row.get("description") or row.get("name"),
				"subtitle": row.get("customer_name") or "",
				"detail": row.get("priority") or "",
				"doctype": "Deadline",
				"docname": row.get("name"),
				"urgency": "red" if dias is not None and dias < 0 else "orange" if dias <= 3 else "yellow",
			}
		)

	for row in tasks or []:
		dias = row.get("days_remaining")
		sort_key = f"{row.get('due_date') or hoje} 09:00:00"
		items.append(
			{
				"type": "task",
				"sort_key": sort_key,
				"date": row.get("due_date") or hoje,
				"title": row.get("subject") or row.get("name"),
				"subtitle": row.get("project_title") or "",
				"detail": row.get("status") or "",
				"doctype": "Task",
				"docname": row.get("name"),
				"urgency": "red" if dias is not None and dias < 0 else "orange" if dias == 0 else "gray",
			}
		)

	items.sort(key=lambda item: item.get("sort_key") or "")
	return items


def get_tasks(hoje, limit):
	rows = frappe.get_all(
		"Task",
		filters={"status": ["in", ["A fazer", "Fazendo"]]},
		fields=["name", "subject", "due_date", "status", "project", "customer"],
		order_by="due_date asc, modified desc",
		limit=limit,
	)
	project_map = _project_lookup([r.project for r in rows if r.project])
	for row in rows:
		row["project_title"] = (project_map.get(row.project) or {}).get("title") or ""
		if row.due_date:
			row["days_remaining"] = date_diff(row.due_date, hoje)
		else:
			row["days_remaining"] = None
	return rows


def get_recent_communications(limit):
	rows = frappe.get_all(
		"Communication Log",
		fields=["name", "subject", "communication_type", "communication_date", "customer", "project"],
		order_by="communication_date desc",
		limit=limit,
	)
	customer_map = _customer_name_lookup([r.customer for r in rows if r.customer])
	for row in rows:
		row["customer_name"] = customer_map.get(row.customer, row.customer or "")
	return rows


def get_hours_summary(hoje):
	week_start = add_days(hoje, -7)
	month_start = get_first_day(hoje)
	month_end = get_last_day(hoje)
	week_rows = frappe.get_all(
		"Time Log",
		filters={"log_date": ["between", [week_start, hoje]]},
		fields=["duration_minutes"],
		limit=LIST_LIMIT_MAX,
	)
	month_rows = frappe.get_all(
		"Time Log",
		filters={"log_date": ["between", [month_start, month_end]]},
		fields=["duration_minutes"],
		limit=LIST_LIMIT_MAX,
	)
	week_hours = round(sum(flt(r.duration_minutes or 0) for r in week_rows) / 60, 1)
	month_hours = round(sum(flt(r.duration_minutes or 0) for r in month_rows) / 60, 1)
	return {
		"week_hours": week_hours,
		"month_hours": month_hours,
	}


def get_hours_period(hoje, period_end):
	rows = frappe.get_all(
		"Time Log",
		filters={"log_date": ["between", [hoje, period_end]]},
		fields=["duration_minutes"],
		limit_page_length=LIST_LIMIT_MAX,
	)
	return round(sum(flt(r.duration_minutes or 0) for r in rows) / 60, 1)
