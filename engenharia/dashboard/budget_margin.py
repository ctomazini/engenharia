"""Visão macro de orçamento e margem por obra para o eng-dashboard."""

from __future__ import annotations

import frappe
from frappe.query_builder.functions import Coalesce, Sum
from frappe.utils import flt

from engenharia.dashboard._helpers import LIST_LIMIT_MAX
from engenharia.engenharia.api.costs import build_consolidated_costs_summary_batch

_TOP_N = 10
_ACTIVE_STATUSES = ("Orçamento", "Em andamento", "Paralisada")


def build_budget_overview() -> dict:
	"""Top 10 obras com maior desvio orçamentário (realizado acima do orçado)."""
	projects = frappe.get_all(
		"Construction Project",
		filters={
			"status": ["in", list(_ACTIVE_STATUSES)],
			"spec_project_total": [">", 0],
		},
		fields=["name", "title", "status", "spec_project_total"],
		limit_page_length=LIST_LIMIT_MAX,
	)
	if not projects:
		return _empty_budget_overview()

	project_names = [row.name for row in projects]
	all_costs = build_consolidated_costs_summary_batch(project_names)

	rows: list[dict] = []
	total_budget = 0.0
	total_realized = 0.0
	projects_over_budget = 0

	for project in projects:
		budget = flt(project.spec_project_total)
		costs = all_costs.get(project.name) or {}
		realized = flt(costs.get("total_amount"))
		paid = flt(costs.get("total_paid"))
		variance = realized - budget
		used_pct = round((realized / budget * 100), 1) if budget else 0.0

		total_budget += budget
		total_realized += realized
		if realized > budget:
			projects_over_budget += 1

		rows.append(
			{
				"project": project.name,
				"title": project.title or project.name,
				"budget": budget,
				"realized": realized,
				"paid": paid,
				"variance": variance,
				"used_pct": used_pct,
			}
		)

	rows.sort(key=lambda row: row["variance"], reverse=True)
	return {
		"items": rows[:_TOP_N],
		"totals": {
			"total_budget": total_budget,
			"total_realized": total_realized,
			"total_variance": total_realized - total_budget,
			"projects_over_budget": projects_over_budget,
		},
	}


def build_margin_by_project() -> dict:
	"""Top 10 obras por margem realizada (receita recebida − custos pagos)."""
	projects = frappe.get_all(
		"Construction Project",
		filters={"status": ["in", list(_ACTIVE_STATUSES)]},
		fields=["name", "title", "status"],
		limit_page_length=LIST_LIMIT_MAX,
	)
	if not projects:
		return _empty_margin_by_project()

	project_names = [row.name for row in projects]
	received_by_project = _received_by_project(project_names)
	all_costs = build_consolidated_costs_summary_batch(project_names)

	rows: list[dict] = []
	total_received = 0.0
	total_paid = 0.0

	for project in projects:
		received = flt(received_by_project.get(project.name))
		if not received:
			continue

		costs = all_costs.get(project.name) or {}
		paid = flt(costs.get("total_paid"))
		margin = received - paid
		margin_pct = round((margin / received * 100), 1) if received else 0.0

		total_received += received
		total_paid += paid
		rows.append(
			{
				"project": project.name,
				"title": project.title or project.name,
				"received": received,
				"total_paid": paid,
				"margin": margin,
				"margin_pct": margin_pct,
			}
		)

	rows.sort(key=lambda row: row["margin"], reverse=True)
	return {
		"items": rows[:_TOP_N],
		"totals": {
			"total_received": total_received,
			"total_paid": total_paid,
			"total_margin": total_received - total_paid,
		},
	}


def _received_by_project(project_names: list[str]) -> dict[str, float]:
	if not project_names:
		return {}

	payment = frappe.qb.DocType("Payment")
	rows = (
		frappe.qb.from_(payment)
		.select(
			payment.project,
			Sum(Coalesce(payment.received_amount, payment.amount)).as_("received"),
		)
		.where(payment.project.isin(project_names))
		.where(payment.status == "Recebido")
		.groupby(payment.project)
	).run(as_dict=True)

	return {row.project: flt(row.received) for row in rows if row.project}


def _empty_budget_overview() -> dict:
	return {
		"items": [],
		"totals": {
			"total_budget": 0.0,
			"total_realized": 0.0,
			"total_variance": 0.0,
			"projects_over_budget": 0,
		},
	}


def _empty_margin_by_project() -> dict:
	return {
		"items": [],
		"totals": {
			"total_received": 0.0,
			"total_paid": 0.0,
			"total_margin": 0.0,
		},
	}
