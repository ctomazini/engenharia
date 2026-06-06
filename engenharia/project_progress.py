"""Cálculo de avanço físico global da obra a partir das etapas."""

from __future__ import annotations

import frappe
from frappe.utils import flt


def calculate_physical_progress(project: str) -> float:
	stages = frappe.get_all(
		"Project Stage",
		filters={"project": project},
		fields=["progress", "weight"],
		limit=500,
	)
	if not stages:
		return 0

	total_weight = sum(flt(stage.weight) or 1 for stage in stages)
	if not total_weight:
		return 0

	weighted_sum = sum(flt(stage.progress) * (flt(stage.weight) or 1) for stage in stages)
	return round(weighted_sum / total_weight, 1)


def sync_project_physical_progress(project: str | None) -> float:
	if not project:
		return 0

	progress = calculate_physical_progress(project)
	frappe.db.set_value(
		"Construction Project",
		project,
		"physical_progress",
		progress,
		update_modified=False,
	)
	return progress


def on_project_stage_update(doc, method=None):
	if doc.project:
		sync_project_physical_progress(doc.project)
