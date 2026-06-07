import frappe

from engenharia.dashboard import get as _get_dashboard_data
from engenharia.dashboard.financial import mark_payment_received as _mark_payment_received


@frappe.whitelist()
def get_dashboard_data(
	limit_start: int = 0,
	limit: int | None = None,
	limit_page_length: int | None = None,
	period_days: int = 7,
	periodo_dias: int | None = None,
	list_limit: int = 5,
	list_limits: dict | str | None = None,
) -> dict:
	frappe.has_permission("Construction Project", "read", throw=True)
	return _get_dashboard_data(
		limit_start=limit_start,
		limit=limit,
		limit_page_length=limit_page_length,
		period_days=period_days,
		periodo_dias=periodo_dias,
		list_limit=list_limit,
		list_limits=list_limits,
	)


@frappe.whitelist()
def mark_payment_received(payment_name: str, received_date: str | None = None):
	frappe.has_permission("Payment", "write", throw=True)
	return _mark_payment_received(payment_name, received_date)
