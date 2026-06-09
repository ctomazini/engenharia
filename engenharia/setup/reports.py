import json
import os

import frappe

REPORT_JSON_PATHS = (
	"work_cost_by_project/work_cost_by_project.json",
	"work_cost_by_category/work_cost_by_category.json",
	"cash_flow/cash_flow.json",
	"projects_by_status/projects_by_status.json",
	"project_margin/project_margin.json",
	"consolidated_cost/consolidated_cost.json",
)

_REPORT_SYNC_FIELDS = (
	"ref_doctype",
	"report_type",
	"module",
	"is_standard",
	"report_name",
	"disabled",
	"add_total_row",
)


def _import_report_json(path):
	data = None
	with open(path) as f:
		data = json.load(f)
	name = data.get("name")
	if not name:
		frappe.import_doc(path)
		return

	if frappe.db.exists("Report", name):
		doc = frappe.get_doc("Report", name)
		for field in _REPORT_SYNC_FIELDS:
			if field in data:
				doc.set(field, data[field])
		doc.save(ignore_permissions=True)  # setup: sincroniza reports do app
	else:
		frappe.import_doc(path)


def ensure_engenharia_reports():
	"""Sincroniza Script Reports do app (idempotente)."""
	base = frappe.get_app_path("engenharia", "engenharia", "report")
	for rel in REPORT_JSON_PATHS:
		path = os.path.join(base, rel)
		if os.path.exists(path):
			_import_report_json(path)

	frappe.clear_cache()
	frappe.db.commit()  # setup: sincroniza reports no migrate
