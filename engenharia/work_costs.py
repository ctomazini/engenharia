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
