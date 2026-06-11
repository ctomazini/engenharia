"""Hub de dados por obra — alimenta painéis visuais do Construction Project."""

from __future__ import annotations

import frappe
from frappe.utils import date_diff, flt, getdate, today

from engenharia.engenharia.api.costs import build_consolidated_costs, build_consolidated_costs_summary
from engenharia.work_costs import get_project_outstanding_payable


@frappe.whitelist()
def get_project_hub_data(project: str) -> dict:
	"""Retorna dados agregados para os painéis do hub."""
	frappe.has_permission("Construction Project", "read", throw=True)

	is_manager = "Engenharia Manager" in frappe.get_roles()

	data: dict = {
		"stages": _get_stages(project),
		"deadlines": _get_deadlines(project),
		"permits": _get_permits(project),
		"tasks": _get_tasks(project),
		"communications": _get_communications(project),
		"measurements": _get_measurements(project),
		"timelogs": _get_timelogs(project),
		"documents": _get_documents(project),
	}

	if is_manager:
		data["financial"] = _get_financial(project)

	return data


@frappe.whitelist()
def get_project_counts(project: str) -> dict:
	"""Contadores rápidos de todos os satélites — para barra resumo."""
	frappe.has_permission("Construction Project", "read", throw=True)

	doctypes = {
		"stages": ("Project Stage", "project"),
		"contracts": ("Engineering Contract", "project"),
		"payments": ("Payment", "project"),
		"costs": ("Work Cost", "project"),
		"subcontracts": ("Subcontract", "project"),
		"reimbursables": ("Reimbursable Expense", "project"),
		"commissions": ("Commission", "construction_project"),
		"deadlines": ("Deadline", "project"),
		"permits": ("Permit", "project"),
		"tasks": ("Task", "project"),
		"communications": ("Communication Log", "project"),
		"timelogs": ("Time Log", "project"),
		"measurements": ("Construction Measurement", "project"),
		"items": ("Project Item", "project"),
		"documents": ("Project Document", "project"),
	}

	return {
		key: frappe.db.count(doctype, {fieldname: project})
		for key, (doctype, fieldname) in doctypes.items()
	}


def _get_stages(project: str) -> list[dict]:
	stages = frappe.get_all(
		"Project Stage",
		filters={"project": project},
		fields=[
			"name",
			"stage_type",
			"status",
			"progress",
			"weight",
			"order",
			"start_date",
			"expected_end",
		],
		order_by="order asc",
		limit=100,
	)
	total_weight = sum(flt(stage.weight) for stage in stages)
	for stage in stages:
		stage["total_weight"] = round(total_weight, 2)
	return stages


def _get_deadlines(project: str) -> list[dict]:
	deadlines = frappe.get_all(
		"Deadline",
		filters={"project": project},
		fields=["name", "title", "due_date", "status", "public_agency"],
		order_by="due_date asc",
		limit=50,
	)
	current = getdate(today())
	for deadline in deadlines:
		if deadline.due_date:
			diff = date_diff(deadline.due_date, current)
			deadline["days_remaining"] = diff
			if deadline.status in ("Concluído", "Cumprido"):
				deadline["urgency"] = "done"
			elif diff < 0:
				deadline["urgency"] = "overdue"
			elif diff <= 7:
				deadline["urgency"] = "urgent"
			else:
				deadline["urgency"] = "normal"
		else:
			deadline["days_remaining"] = None
			deadline["urgency"] = "normal"
	return deadlines


def _get_permits(project: str) -> list[dict]:
	return frappe.get_all(
		"Permit",
		filters={"project": project},
		fields=[
			"name",
			"title",
			"permit_type",
			"status",
			"permit_number",
			"protocol_date",
			"expiry_date",
		],
		order_by="expiry_date asc",
		limit=50,
	)


def _get_tasks(project: str) -> list[dict]:
	return frappe.get_all(
		"Task",
		filters={"project": project, "status": ["not in", ["Feito", "Cancelada"]]},
		fields=["name", "subject", "status", "priority", "due_date"],
		order_by="due_date asc",
		limit=20,
	)


def _get_communications(project: str) -> list[dict]:
	return frappe.get_all(
		"Communication Log",
		filters={"project": project},
		fields=["name", "title", "communication_type", "communication_date", "subject"],
		order_by="communication_date desc",
		limit=10,
	)


def _get_measurements(project: str) -> list[dict]:
	return frappe.get_all(
		"Construction Measurement",
		filters={"project": project},
		fields=["name", "title", "measurement_date", "reference_period"],
		order_by="measurement_date desc",
		limit=10,
	)


def _get_documents(project: str) -> list[dict]:
	return frappe.get_all(
		"Project Document",
		filters={"project": project},
		fields=[
			"name",
			"title",
			"category",
			"status",
			"source",
			"version",
			"file",
			"creation",
		],
		order_by="creation desc",
		limit=50,
	)


def _get_timelogs(project: str) -> list[dict]:
	return frappe.get_all(
		"Time Log",
		filters={"project": project},
		fields=["name", "activity", "log_date", "duration_hours"],
		order_by="log_date desc",
		limit=20,
	)


def _get_financial(project: str) -> dict:
	contracts = frappe.get_all(
		"Engineering Contract",
		filters={"project": project},
		fields=["name", "title", "current_value", "status"],
		limit=20,
	)

	inst = frappe.qb.DocType("Engineering Contract Installment")
	cont = frappe.qb.DocType("Engineering Contract")
	installments = (
		frappe.qb.from_(inst)
		.join(cont)
		.on(inst.parent == cont.name)
		.select(
			inst.name,
			inst.due_date,
			inst.amount,
			inst.status,
			inst.idx,
			cont.name.as_("contract"),
			cont.title.as_("contract_title"),
		)
		.where(cont.project == project)
		.orderby(inst.due_date)
		.limit(100)
	).run(as_dict=True)

	payments = frappe.get_all(
		"Payment",
		filters={"project": project},
		fields=["name", "title", "amount", "received_date", "status"],
		order_by="received_date desc",
		limit=50,
	)

	costs = frappe.get_all(
		"Work Cost",
		filters={"project": project},
		fields=["name", "title", "amount", "cost_category", "status"],
		order_by="creation desc",
		limit=50,
	)

	subcontracts = frappe.get_all(
		"Subcontract",
		filters={"project": project},
		fields=["name", "title", "total_value", "total_paid", "status"],
		limit=20,
	)

	commissions = frappe.get_all(
		"Commission",
		filters={"construction_project": project},
		fields=["name", "title", "total_value", "status"],
		limit=20,
	)

	reimbursables = frappe.get_all(
		"Reimbursable Expense",
		filters={"project": project},
		fields=["name", "title", "amount", "status"],
		limit=20,
	)

	total_contracted = sum(flt(contract.current_value) for contract in contracts)
	total_received = sum(flt(payment.amount) for payment in payments if payment.status == "Recebido")
	total_commissions = sum(flt(commission.total_value) for commission in commissions)
	total_reimbursable = sum(flt(expense.amount) for expense in reimbursables)

	cost_summary = build_consolidated_costs(project)["summary"]
	office_paid = build_consolidated_costs_summary(project, office_only=True)["total_paid"]
	budget_total = flt(frappe.db.get_value("Construction Project", project, "spec_project_total"))
	outstanding_payable = get_project_outstanding_payable(project)

	return {
		"contracts": contracts,
		"installments": installments,
		"payments": payments,
		"costs": costs,
		"subcontracts": subcontracts,
		"commissions": commissions,
		"reimbursables": reimbursables,
		"summary": {
			"total_contracted": total_contracted,
			"total_received": total_received,
			"total_pending": total_contracted - total_received,
			"budget_total": budget_total,
			"total_realized_committed": flt(cost_summary.get("total_amount")),
			"total_realized_paid": flt(cost_summary.get("total_paid")),
			"total_realized_outstanding": flt(cost_summary.get("total_outstanding")),
			"outstanding_payable": outstanding_payable,
			"total_commissions": total_commissions,
			"total_reimbursable": total_reimbursable,
			"margin": total_received - office_paid,
			# Compat legado (KPI antigo)
			"total_costs": flt(cost_summary.get("total_paid")),
			"total_subcontracts": 0,
		},
	}
