from frappe import _
from frappe.utils import add_days, date_diff

from engenharia.dashboard.timeline import build_timeline


def _relative_when(hoje, date_value):
	if not date_value:
		return _("Sem data")
	dias = date_diff(date_value, hoje)
	if dias == 0:
		return _("Hoje")
	if dias == 1:
		return _("Amanhã")
	if dias == -1:
		return _("Ontem")
	if dias < 0:
		return _("Há {0} dias").format(abs(dias))
	return _("Em {0} dias").format(dias)


def _icon_for_type(item_type):
	return {
		"deadline": "clock-alert",
		"task": "list-todo",
		"payment": "circle-dollar-sign",
		"permit": "clipboard-check",
	}.get(item_type, "calendar")


def build_agenda(hoje, period_end, deadlines, tasks, payments=None):
	items = build_timeline(hoje, period_end, deadlines, tasks)

	for row in payments or []:
		dias = row.get("days_remaining")
		if dias is None and row.get("due_date"):
			dias = date_diff(row.get("due_date"), hoje)
		items.append(
			{
				"type": "payment",
				"sort_key": f"{row.get('due_date') or hoje} 08:00:00",
				"date": row.get("due_date"),
				"title": row.get("title") or row.get("name"),
				"subtitle": row.get("customer_name") or "",
				"detail": row.get("status") or "",
				"doctype": "Payment",
				"docname": row.get("name"),
				"urgency": "red"
				if row.get("status") == "Vencido"
				else "orange"
				if dias is not None and dias <= 3
				else "yellow",
				"amount": row.get("valor_total") or row.get("amount"),
			}
		)

	items.sort(key=lambda item: item.get("sort_key") or "")
	for item in items:
		item["when_label"] = _relative_when(hoje, item.get("date"))
		item["icon"] = _icon_for_type(item.get("type"))
	return items


def build_day_strip(hoje, period_days, agenda_items):
	days = []
	for offset in range(min(period_days, 7)):
		day = add_days(hoje, offset)
		day_items = [row for row in agenda_items if row.get("date") == day]
		days.append(
			{
				"date": day,
				"label": _relative_when(hoje, day),
				"count": len(day_items),
				"tone": "red"
				if any(row.get("urgency") == "red" for row in day_items)
				else "orange"
				if day_items
				else "gray",
			}
		)
	return days
