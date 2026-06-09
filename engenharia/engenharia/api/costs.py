"""API de custos consolidados por obra."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, getdate

from engenharia.work_costs import FUNDED_BY_OFFICE

MAX_ITEMS = 500

SOURCE_WORK_COST = "work_cost"
SOURCE_REIMBURSABLE = "reimbursable_expense"
SOURCE_SUBCONTRACT = "subcontract"

SOURCE_META = {
	SOURCE_WORK_COST: {
		"label": _("Compra avulsa"),
		"doctype": "Work Cost",
	},
	SOURCE_REIMBURSABLE: {
		"label": _("Despesa Reembolsável"),
		"doctype": "Reimbursable Expense",
	},
	SOURCE_SUBCONTRACT: {
		"label": _("Subcontrato"),
		"doctype": "Subcontract",
	},
}


@frappe.whitelist()
def get_consolidated_costs(project: str) -> dict:
	frappe.has_permission("Construction Project", "read", throw=True)
	return build_consolidated_costs(project)


def build_consolidated_costs(project: str, filters: dict | None = None) -> dict:
	filters = frappe._dict(filters or {})
	items = _fetch_normalized_items(project)
	items = _apply_item_filters(items, filters)
	items.sort(key=lambda row: getdate(row.get("date") or "1900-01-01"), reverse=True)
	items = items[:MAX_ITEMS]
	summary = _build_summary(items)
	return {"items": items, "summary": summary}


def build_consolidated_costs_summary(project: str, office_only: bool = False) -> dict:
	"""Totais consolidados da obra; office_only restringe a fluxo do escritório."""
	items = _fetch_normalized_items(project)
	if office_only:
		items = [row for row in items if _is_office_cash_flow_item(row)]
	return _build_summary(items)


def _is_office_cash_flow_item(row: dict) -> bool:
	if row.get("source") == SOURCE_REIMBURSABLE:
		return True
	return row.get("funded_by") == FUNDED_BY_OFFICE


def _fetch_normalized_items(project: str) -> list[dict]:
	items: list[dict] = []
	items.extend(_fetch_work_costs(project))
	items.extend(_fetch_reimbursable_expenses(project))
	items.extend(_fetch_subcontracts(project))
	return items


def _fetch_work_costs(project: str) -> list[dict]:
	wc = frappe.qb.DocType("Work Cost")
	cat = frappe.qb.DocType("Cost Category")
	sup = frappe.qb.DocType("Supplier")
	stg = frappe.qb.DocType("Project Stage")

	rows = (
		frappe.qb.from_(wc)
		.left_join(cat)
		.on(wc.cost_category == cat.name)
		.left_join(sup)
		.on(wc.supplier == sup.name)
		.left_join(stg)
		.on(wc.stage == stg.name)
		.select(
			wc.name,
			wc.date,
			wc.description,
			wc.cost_category,
			cat.category_name.as_("category_label"),
			wc.supplier,
			sup.supplier_name.as_("supplier_label"),
			wc.stage,
			stg.stage_type.as_("stage_label"),
			wc.funded_by,
			wc.amount,
			wc.total_paid,
			wc.outstanding,
			wc.status,
		)
		.where(wc.project == project)
		.where(wc.status != "Cancelled")
		.limit(MAX_ITEMS)
	).run(as_dict=True)

	return [_normalize_work_cost(row) for row in rows]


def _fetch_reimbursable_expenses(project: str) -> list[dict]:
	re = frappe.qb.DocType("Reimbursable Expense")
	cat = frappe.qb.DocType("Cost Category")
	sup = frappe.qb.DocType("Supplier")

	rows = (
		frappe.qb.from_(re)
		.left_join(cat)
		.on(re.expense_category == cat.name)
		.left_join(sup)
		.on(re.supplier == sup.name)
		.select(
			re.name,
			re.creation,
			re.description,
			re.expense_category,
			cat.category_name.as_("category_label"),
			re.supplier,
			sup.supplier_name.as_("supplier_label"),
			re.amount,
			re.total_office_paid,
			re.office_outstanding,
			re.status,
		)
		.where(re.project == project)
		.where(re.status != "Cancelado")
		.limit(MAX_ITEMS)
	).run(as_dict=True)

	return [_normalize_reimbursable(row) for row in rows]


def _fetch_subcontracts(project: str) -> list[dict]:
	sc = frappe.qb.DocType("Subcontract")
	cat = frappe.qb.DocType("Cost Category")
	sup = frappe.qb.DocType("Supplier")
	stg = frappe.qb.DocType("Project Stage")

	rows = (
		frappe.qb.from_(sc)
		.left_join(cat)
		.on(sc.cost_category == cat.name)
		.left_join(sup)
		.on(sc.supplier == sup.name)
		.left_join(stg)
		.on(sc.stage == stg.name)
		.select(
			sc.name,
			sc.creation,
			sc.description,
			sc.title,
			sc.cost_category,
			cat.category_name.as_("category_label"),
			sc.supplier,
			sup.supplier_name.as_("supplier_label"),
			sc.stage,
			stg.stage_type.as_("stage_label"),
			sc.funded_by,
			sc.total_value,
			sc.total_paid,
			sc.outstanding,
			sc.status,
		)
		.where(sc.project == project)
		.where(sc.status != "Cancelled")
		.limit(MAX_ITEMS)
	).run(as_dict=True)

	return [_normalize_subcontract(row) for row in rows]


def _normalize_work_cost(row: dict) -> dict:
	amount = flt(row.amount)
	paid = flt(row.total_paid)
	outstanding = flt(row.outstanding)
	return _base_item(
		source=SOURCE_WORK_COST,
		name=row.name,
		date=row.date,
		description=row.description or row.name,
		category=row.cost_category,
		category_label=row.category_label,
		supplier=row.supplier,
		supplier_label=row.supplier_label,
		stage=row.stage,
		stage_label=row.stage_label,
		funded_by=row.funded_by,
		amount=amount,
		paid=paid,
		outstanding=outstanding,
		status=row.status,
	)


def _normalize_reimbursable(row: dict) -> dict:
	amount = flt(row.amount)
	paid = flt(row.total_office_paid)
	outstanding = flt(row.office_outstanding)
	return _base_item(
		source=SOURCE_REIMBURSABLE,
		name=row.name,
		date=getdate(row.creation),
		description=row.description or row.name,
		category=row.expense_category,
		category_label=row.category_label,
		supplier=row.supplier,
		supplier_label=row.supplier_label,
		stage=None,
		stage_label=None,
		funded_by=None,
		amount=amount,
		paid=paid,
		outstanding=outstanding,
		status=row.status,
	)


def _normalize_subcontract(row: dict) -> dict:
	amount = flt(row.total_value)
	paid = flt(row.total_paid)
	outstanding = flt(row.outstanding)
	description = row.description or row.title or row.name
	return _base_item(
		source=SOURCE_SUBCONTRACT,
		name=row.name,
		date=getdate(row.creation),
		description=description,
		category=row.cost_category,
		category_label=row.category_label,
		supplier=row.supplier,
		supplier_label=row.supplier_label,
		stage=row.stage,
		stage_label=row.stage_label,
		funded_by=row.funded_by,
		amount=amount,
		paid=paid,
		outstanding=outstanding,
		status=row.status,
	)


def _base_item(**kwargs) -> dict:
	source = kwargs.pop("source")
	meta = SOURCE_META[source]
	category_link = kwargs.pop("category", None)
	category_label = kwargs.pop("category_label", None) or category_link or _("Sem categoria")
	supplier_link = kwargs.pop("supplier", None)
	supplier_label = kwargs.pop("supplier_label", None) or supplier_link or ""
	stage_link = kwargs.pop("stage", None)
	stage_label = kwargs.pop("stage_label", None) or stage_link or ""
	return {
		"source": source,
		"source_label": meta["label"],
		"source_doctype": meta["doctype"],
		"category": category_label,
		"category_link": category_link,
		"supplier": supplier_label,
		"supplier_link": supplier_link,
		"stage": stage_label,
		"stage_link": stage_link,
		**kwargs,
	}


def _apply_item_filters(items: list[dict], filters) -> list[dict]:
	result = items
	if filters.get("from_date"):
		from_date = getdate(filters.from_date)
		result = [row for row in result if row.get("date") and getdate(row["date"]) >= from_date]
	if filters.get("to_date"):
		to_date = getdate(filters.to_date)
		result = [row for row in result if row.get("date") and getdate(row["date"]) <= to_date]
	if filters.get("cost_type"):
		result = [row for row in result if row.get("source") == filters.cost_type]
	if filters.get("category"):
		result = [row for row in result if row.get("category_link") == filters.category]
	if filters.get("supplier"):
		result = [row for row in result if row.get("supplier_link") == filters.supplier]
	if filters.get("stage"):
		result = [row for row in result if row.get("stage_link") == filters.stage]
	if filters.get("funded_by"):
		result = [row for row in result if row.get("funded_by") == filters.funded_by]
	return result


def _build_summary(items: list[dict]) -> dict:
	total_amount = sum(flt(row["amount"]) for row in items)
	total_paid = sum(flt(row["paid"]) for row in items)
	total_outstanding = sum(flt(row["outstanding"]) for row in items)

	by_source: dict[str, dict] = {}
	by_category: dict[str, float] = {}
	by_funded_by: dict[str, float] = {}

	for row in items:
		source_key = row["source_label"]
		source_bucket = by_source.setdefault(
			source_key,
			{"amount": 0, "paid": 0, "outstanding": 0, "count": 0},
		)
		source_bucket["amount"] += flt(row["amount"])
		source_bucket["paid"] += flt(row["paid"])
		source_bucket["outstanding"] += flt(row["outstanding"])
		source_bucket["count"] += 1

		category_key = row.get("category") or _("Sem categoria")
		by_category[category_key] = by_category.get(category_key, 0) + flt(row["amount"])

		funded_key = row.get("funded_by") or _("—")
		by_funded_by[funded_key] = by_funded_by.get(funded_key, 0) + flt(row["amount"])

	return {
		"total_amount": total_amount,
		"total_paid": total_paid,
		"total_outstanding": total_outstanding,
		"by_source": by_source,
		"by_category": by_category,
		"by_funded_by": by_funded_by,
	}
