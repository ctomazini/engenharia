"""Agregação de custos de obra por dimensão."""

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt

DEFAULT_STATUSES = ("Pago",)
UNCLASSIFIED = "Sem classificação"
FUNDED_BY_OFFICE = "Escritório"
FUNDED_BY_CLIENT = "Cliente"


def office_cash_flow_filters(extra=None):
	"""Filtros para custos que saem do caixa do escritório (Work Cost)."""
	filters = {"funded_by": FUNDED_BY_OFFICE}
	if extra:
		filters.update(extra)
	return filters


def office_subcontract_filters(extra=None):
	"""Filtros para subcontratos pagos pelo escritório."""
	filters = {"funded_by": FUNDED_BY_OFFICE}
	if extra:
		filters.update(extra)
	return filters


def get_firm_work_cost_total(project=None, statuses=None):
	rows = frappe.get_all(
		"Work Cost",
		filters=office_cash_flow_filters(_base_filters(project=project, statuses=statuses)),
		fields=["amount"],
		limit=500,
	)
	return sum(flt(row.amount) for row in rows)


def get_firm_subcontract_payments_month(month_start, month_end):
	"""Total pago em subcontratos do escritório no mês."""
	result = frappe.db.sql(
		"""
		select coalesce(sum(sp.amount), 0)
		from `tabSubcontract Payment` sp
		inner join `tabSubcontract` sc on sc.name = sp.parent
		where sc.funded_by = %s
		  and sc.status != 'Cancelled'
		  and sp.payment_date between %s and %s
		""",
		(FUNDED_BY_OFFICE, month_start, month_end),
	)
	return flt(result[0][0] if result else 0)


def get_firm_subcontract_payment_count_month(month_start, month_end):
	result = frappe.db.sql(
		"""
		select count(sp.name)
		from `tabSubcontract Payment` sp
		inner join `tabSubcontract` sc on sc.name = sp.parent
		where sc.funded_by = %s
		  and sc.status != 'Cancelled'
		  and sp.payment_date between %s and %s
		""",
		(FUNDED_BY_OFFICE, month_start, month_end),
	)
	return int(result[0][0] if result else 0)


def get_subcontract_payments_by_category_month(month_start, month_end):
	"""Pagamentos de subcontrato do escritório agrupados por categoria de custo."""
	rows = frappe.db.sql(
		"""
		select sc.cost_category, coalesce(sum(sp.amount), 0) as amount
		from `tabSubcontract Payment` sp
		inner join `tabSubcontract` sc on sc.name = sp.parent
		where sc.funded_by = %s
		  and sc.status != 'Cancelled'
		  and sp.payment_date between %s and %s
		group by sc.cost_category
		""",
		(FUNDED_BY_OFFICE, month_start, month_end),
		as_dict=True,
	)
	totals: dict[str, float] = {}
	for row in rows:
		key = row.cost_category or _("Sem categoria")
		totals[key] = flt(row.amount)
	return totals


def get_firm_month_outflows(month_start, month_end):
	"""Saídas do escritório no mês: Work Cost + pagamentos de subcontrato."""
	work_rows = frappe.get_all(
		"Work Cost",
		filters=office_cash_flow_filters(
			{
				"status": ["!=", "Cancelado"],
				"date": ["between", [month_start, month_end]],
			}
		),
		fields=["amount"],
		limit=500,
	)
	work_amount = sum(flt(row.amount) for row in work_rows)
	sub_amount = get_firm_subcontract_payments_month(month_start, month_end)
	sub_count = get_firm_subcontract_payment_count_month(month_start, month_end)
	return {
		"amount": work_amount + sub_amount,
		"count": len(work_rows) + sub_count,
		"work_cost_amount": work_amount,
		"subcontract_amount": sub_amount,
	}


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


def get_subcontract_paid_totals_by_project(project=None, office_funded_only=False):
	"""Retorna total_paid de Subcontract agrupado por obra (status != Cancelled)."""
	filters = {"status": ["!=", "Cancelled"]}
	if office_funded_only:
		filters["funded_by"] = FUNDED_BY_OFFICE
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
	"""Custos na obra: Work Cost (Pago) + Subcontract.total_paid (todos os financiadores)."""
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


def get_subcontract_outstanding_total(office_funded_only=True):
	"""Saldo a pagar a prestadores (subcontratos não cancelados)."""
	conditions = "status != 'Cancelled'"
	if office_funded_only:
		conditions += f" and funded_by = {frappe.db.escape(FUNDED_BY_OFFICE)}"
	result = frappe.db.sql(
		f"""
		select coalesce(sum(outstanding), 0)
		from `tabSubcontract`
		where {conditions}
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
