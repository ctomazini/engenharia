"""Agregação de custos de obra por dimensão."""

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt

DEFAULT_STATUSES = ("Pago",)
UNCLASSIFIED = "Sem classificação"


def _base_filters(project=None, statuses=None):
	filters = {"status": ["in", list(statuses or DEFAULT_STATUSES)]}
	if project:
		filters["project"] = project
	return filters


def get_work_cost_totals_by_category(project=None, statuses=None):
	"""Retorna totais de Work Cost agrupados por cost_category."""
	return _aggregate_by_field("cost_category", project=project, statuses=statuses)


def get_work_cost_totals_by_supplier(project=None, statuses=None):
	"""Retorna totais de Work Cost agrupados por supplier."""
	return _aggregate_by_field("supplier", project=project, statuses=statuses)


def get_work_cost_totals_by_stage(project=None, statuses=None):
	"""Retorna totais de Work Cost agrupados por stage."""
	return _aggregate_by_field("stage", project=project, statuses=statuses)


def get_subcontract_paid_totals_by_project(project=None):
	"""Retorna total_paid de Subcontract agrupado por obra (status != Cancelled)."""
	filters = {"status": ["!=", "Cancelled"]}
	if project:
		filters["project"] = project
	rows = frappe.get_all(
		"Subcontract",
		filters=filters,
		fields=["project", "total_paid"],
		limit=500,
	)
	totals = defaultdict(float)
	for row in rows:
		if not row.project:
			continue
		totals[row.project] += flt(row.total_paid)
	return dict(totals)


def get_combined_project_cost(project):
	"""Custos pagos na obra: Work Cost (Pago) + Subcontract.total_paid."""
	work_rows = frappe.get_all(
		"Work Cost",
		filters={"project": project, "status": "Pago"},
		fields=["amount"],
		limit=500,
	)
	sub_rows = frappe.get_all(
		"Subcontract",
		filters={"project": project, "status": ["!=", "Cancelled"]},
		fields=["total_paid"],
		limit=500,
	)
	work_total = sum(flt(row.amount) for row in work_rows)
	sub_total = sum(flt(row.total_paid) for row in sub_rows)
	return work_total + sub_total


def get_subcontract_outstanding_total():
	"""Saldo total a pagar a prestadores (subcontratos não cancelados)."""
	result = frappe.db.sql(
		"""
		select coalesce(sum(outstanding), 0)
		from `tabSubcontract`
		where status != 'Cancelled'
		"""
	)
	return flt(result[0][0] if result else 0)


def _aggregate_by_field(fieldname, project=None, statuses=None):
	rows = frappe.get_all(
		"Work Cost",
		filters=_base_filters(project=project, statuses=statuses),
		fields=[fieldname, "amount"],
		limit=500,
	)
	totals = defaultdict(float)
	for row in rows:
		key = row.get(fieldname) or UNCLASSIFIED
		totals[key] += flt(row.amount)
	return dict(totals)
