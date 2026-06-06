import frappe
from frappe.query_builder import functions as fn
from frappe.utils import flt

from engenharia.dashboard._helpers import _project_lookup


def get_commission_kpis() -> dict:
	"""KPIs agregados de comissões."""
	Commission = frappe.qb.DocType("Commission")
	result = (
		frappe.qb.from_(Commission)
		.select(
			fn.Sum(Commission.total_value).as_("total"),
			fn.Sum(Commission.total_paid).as_("total_paid"),
			fn.Sum(Commission.outstanding).as_("total_outstanding"),
		)
		.where(Commission.status != "Cancelled")
	).run(as_dict=True)[0]

	return {
		"commission_total": flt(result.total),
		"commission_paid": flt(result.total_paid),
		"commission_outstanding": flt(result.total_outstanding),
	}


def get_pending_commissions(limit: int = 10) -> list[dict]:
	"""Comissões abertas ou parcialmente pagas."""
	rows = frappe.get_all(
		"Commission",
		filters={"status": ["in", ["Open", "Partially Paid"]]},
		fields=[
			"name",
			"title",
			"construction_project",
			"supplier_name",
			"total_value",
			"outstanding",
			"status",
		],
		order_by="outstanding desc",
		limit=limit,
	)
	project_map = _project_lookup([row.construction_project for row in rows if row.construction_project])
	for row in rows:
		project = project_map.get(row.construction_project) or {}
		row["project_title"] = project.get("title") or row.construction_project or ""
	return rows
