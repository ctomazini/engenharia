"""Agregação de custos de obra por dimensão."""

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt

DEFAULT_STATUSES = ("Paid",)
UNCLASSIFIED = "Sem classificação"
FUNDED_BY_OFFICE = "Escritório"
FUNDED_BY_CLIENT = "Cliente"
WORK_COST_CANCELLED = "Cancelled"
WORK_COST_PENDING_STATUSES = ("Open", "Partially Paid")


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


def get_firm_work_cost_paid_total(project=None):
	rows = frappe.get_all(
		"Work Cost",
		filters=office_cash_flow_filters(
			{
				"status": ["!=", WORK_COST_CANCELLED],
				**( {"project": project} if project else {}),
			}
		),
		fields=["total_paid"],
		limit=500,
	)
	return sum(flt(row.total_paid) for row in rows)


def get_firm_work_cost_payment_total_month(month_start, month_end):
	result = frappe.db.sql(
		"""
		select coalesce(sum(wcp.amount), 0)
		from `tabWork Cost Payment` wcp
		inner join `tabWork Cost` wc on wc.name = wcp.parent
		where wc.funded_by = %s
		  and wc.status != %s
		  and wcp.payment_date between %s and %s
		""",
		(FUNDED_BY_OFFICE, WORK_COST_CANCELLED, month_start, month_end),
	)
	return flt(result[0][0] if result else 0)


def get_firm_work_cost_payment_count_month(month_start, month_end):
	result = frappe.db.sql(
		"""
		select count(wcp.name)
		from `tabWork Cost Payment` wcp
		inner join `tabWork Cost` wc on wc.name = wcp.parent
		where wc.funded_by = %s
		  and wc.status != %s
		  and wcp.payment_date between %s and %s
		""",
		(FUNDED_BY_OFFICE, WORK_COST_CANCELLED, month_start, month_end),
	)
	return int(result[0][0] if result else 0)


def get_firm_reimbursable_office_payment_total_month(month_start, month_end):
	result = frappe.db.sql(
		"""
		select coalesce(sum(rep.amount), 0)
		from `tabReimbursable Expense Payment` rep
		inner join `tabReimbursable Expense` re on re.name = rep.parent
		where re.status != 'Cancelado'
		  and rep.payment_date between %s and %s
		""",
		(month_start, month_end),
	)
	return flt(result[0][0] if result else 0)


def get_firm_reimbursable_office_payment_count_month(month_start, month_end):
	result = frappe.db.sql(
		"""
		select count(rep.name)
		from `tabReimbursable Expense Payment` rep
		inner join `tabReimbursable Expense` re on re.name = rep.parent
		where re.status != 'Cancelado'
		  and rep.payment_date between %s and %s
		""",
		(month_start, month_end),
	)
	return int(result[0][0] if result else 0)


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
	"""Saídas do escritório no mês: pagamentos de Work Cost, Reembolsável e Subcontrato."""
	work_amount = get_firm_work_cost_payment_total_month(month_start, month_end)
	work_count = get_firm_work_cost_payment_count_month(month_start, month_end)
	reimb_amount = get_firm_reimbursable_office_payment_total_month(month_start, month_end)
	reimb_count = get_firm_reimbursable_office_payment_count_month(month_start, month_end)
	sub_amount = get_firm_subcontract_payments_month(month_start, month_end)
	sub_count = get_firm_subcontract_payment_count_month(month_start, month_end)
	return {
		"amount": work_amount + reimb_amount + sub_amount,
		"count": work_count + reimb_count + sub_count,
		"work_cost_amount": work_amount,
		"reimbursable_amount": reimb_amount,
		"subcontract_amount": sub_amount,
	}


def _base_filters(project=None, statuses=None):
	filters = {"status": ["in", list(statuses or DEFAULT_STATUSES)]}
	if project:
		filters["project"] = project
	return filters


def get_work_cost_totals_by_category(project=None, statuses=None):
	"""Retorna totais pagos de Work Cost agrupados por cost_category."""
	return _aggregate_by_field("cost_category", project=project, statuses=statuses, amount_field="total_paid")


def get_work_cost_totals_by_supplier(project=None, statuses=None):
	"""Retorna totais pagos de Work Cost agrupados por supplier."""
	return _aggregate_by_field("supplier", project=project, statuses=statuses, amount_field="total_paid")


def get_work_cost_totals_by_stage(project=None, statuses=None):
	"""Retorna totais pagos de Work Cost agrupados por stage."""
	return _aggregate_by_field("stage", project=project, statuses=statuses, amount_field="total_paid")


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
	"""Custos pagos na obra: Work Cost.total_paid + Subcontract.total_paid."""
	work_rows = frappe.get_all(
		"Work Cost",
		filters={"project": project, "status": ["!=", WORK_COST_CANCELLED]},
		fields=["total_paid"],
		limit=500,
	)
	sub_rows = frappe.get_all(
		"Subcontract",
		filters={"project": project, "status": ["!=", "Cancelled"]},
		fields=["total_paid"],
		limit=500,
	)
	work_total = sum(flt(row.total_paid) for row in work_rows)
	sub_total = sum(flt(row.total_paid) for row in sub_rows)
	return work_total + sub_total


def get_project_outstanding_payable(project: str, office_funded_only: bool = True) -> float:
	"""Saldo a pagar na obra: Work Cost + Subcontract (escritório por padrão)."""
	filters = {"project": project, "status": ["!=", WORK_COST_CANCELLED]}
	if office_funded_only:
		filters["funded_by"] = FUNDED_BY_OFFICE
	wc_rows = frappe.get_all("Work Cost", filters=filters, fields=["outstanding"], limit=500)

	sub_filters = {"project": project, "status": ["!=", "Cancelled"]}
	if office_funded_only:
		sub_filters["funded_by"] = FUNDED_BY_OFFICE
	sub_rows = frappe.get_all("Subcontract", filters=sub_filters, fields=["outstanding"], limit=500)

	return sum(flt(row.outstanding) for row in wc_rows) + sum(flt(row.outstanding) for row in sub_rows)


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


def get_work_cost_outstanding_total(office_funded_only=True):
	"""Saldo a pagar em custos avulsos (Work Cost não cancelados)."""
	conditions = f"status != {frappe.db.escape(WORK_COST_CANCELLED)}"
	if office_funded_only:
		conditions += f" and funded_by = {frappe.db.escape(FUNDED_BY_OFFICE)}"
	result = frappe.db.sql(
		f"""
		select coalesce(sum(outstanding), 0)
		from `tabWork Cost`
		where {conditions}
		"""
	)
	return flt(result[0][0] if result else 0)


def _aggregate_by_field(fieldname, project=None, statuses=None, amount_field="total_paid"):
	filters = _base_filters(project=project, statuses=statuses)
	rows = frappe.get_all(
		"Work Cost",
		filters=filters,
		fields=[fieldname, amount_field],
		limit=500,
	)
	totals = defaultdict(float)
	for row in rows:
		key = row.get(fieldname) or UNCLASSIFIED
		totals[key] += flt(row.get(amount_field))
	return dict(totals)


# Compat: relatórios legados que somavam amount com status Pago
get_firm_work_cost_total = get_firm_work_cost_paid_total
