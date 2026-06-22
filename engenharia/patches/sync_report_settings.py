import frappe


def execute():
	"""Sync add_total_row for script reports that show aggregated data.

	Sites that existed before the JSON fix (Bloco 1) still have
	add_total_row=1 in the database. This patch aligns them.
	Idempotent — safe to run multiple times.
	"""
	reports = [
		"budget_vs_actual",
		"project_margin",
		"work_cost_by_project",
		"work_cost_by_category",
	]
	for report_name in reports:
		if frappe.db.exists("Report", report_name):
			frappe.db.set_value("Report", report_name, "add_total_row", 0)
