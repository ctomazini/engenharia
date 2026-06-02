import frappe

from engenharia.dashboard import get as _get_dashboard_data
from engenharia.dashboard.financial import mark_payment_received as _mark_payment_received


@frappe.whitelist()
def get_dashboard_data(
	limit_start=0,
	limit_page_length=20,
	period_days=7,
	list_limit=5,
	list_limits=None,
):
	return _get_dashboard_data(
		limit_start=limit_start,
		limit_page_length=limit_page_length,
		period_days=period_days,
		list_limit=list_limit,
		list_limits=list_limits,
	)


@frappe.whitelist()
def mark_payment_received(payment_name: str, received_date: str | None = None):
	return _mark_payment_received(payment_name, received_date)
