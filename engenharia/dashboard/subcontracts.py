import frappe
from frappe.query_builder import functions as fn
from frappe.utils import flt

from engenharia.dashboard._helpers import _project_lookup
from engenharia.work_costs import FUNDED_BY_OFFICE


def get_subcontract_kpis() -> dict:
	"""KPIs agregados de subcontratos pagos pelo escritório."""
	Subcontract = frappe.qb.DocType("Subcontract")
	result = (
		frappe.qb.from_(Subcontract)
		.select(
			fn.Sum(Subcontract.total_value).as_("total"),
			fn.Sum(Subcontract.total_paid).as_("total_paid"),
			fn.Sum(Subcontract.outstanding).as_("total_outstanding"),
		)
		.where(Subcontract.status != "Cancelled")
		.where(Subcontract.funded_by == FUNDED_BY_OFFICE)
	).run(as_dict=True)[0]

	return {
		"subcontract_total": flt(result.total),
		"subcontract_paid": flt(result.total_paid),
		"subcontract_outstanding": flt(result.total_outstanding),
	}


def get_pending_subcontracts(limit: int = 10) -> list[dict]:
	"""Subcontratos do escritório com saldo a pagar."""
	rows = frappe.get_all(
		"Subcontract",
		filters={
			"status": ["in", ["Open", "Partially Paid"]],
			"funded_by": FUNDED_BY_OFFICE,
		},
		fields=[
			"name",
			"title",
			"project",
			"supplier",
			"total_value",
			"outstanding",
			"status",
		],
		order_by="outstanding desc",
		limit=limit,
	)
	project_map = _project_lookup([row.project for row in rows if row.project])
	supplier_names = {
		s.name: s.supplier_name
		for s in frappe.get_all(
			"Supplier",
			filters={"name": ["in", [r.supplier for r in rows if r.supplier]]},
			fields=["name", "supplier_name"],
			limit=limit,
		)
	}
	for row in rows:
		project = project_map.get(row.project) or {}
		row["project_title"] = project.get("title") or row.project or ""
		row["supplier_name"] = supplier_names.get(row.supplier) or row.supplier or ""
	return rows
