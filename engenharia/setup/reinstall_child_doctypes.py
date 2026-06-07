import os

import frappe
from frappe.modules.import_file import import_file_by_path


CHILD_DOCTYPES = [
	"Engineering Contract Installment",
	"Engineering Contract Amendment",
	"Project Specification",
	"Project Budget Revision",
	"Project Item Parameter",
	"Project Item Output",
	"Project Item Cost Component",
	"Technical Item Field",
	"Technical Item Output",
	"Customer Address",
	"Customer Contact",
	"Document Kit Item",
	"Subcontract Payment",
	"Commission Payment",
	"Construction Measurement Item",
]

PARENT_DOCTYPES_AFTER_CHILD = [
	"Document Kit",
]


def reinstall_child_doctypes():
	"""Garante que DocTypes istable=1 existam no banco após migrate."""
	base = frappe.get_app_path("engenharia", "engenharia", "doctype")
	reinstalled = []

	for dt in CHILD_DOCTYPES + PARENT_DOCTYPES_AFTER_CHILD:
		if frappe.db.exists("DocType", dt):
			continue
		dt_path = os.path.join(base, frappe.scrub(dt), f"{frappe.scrub(dt)}.json")
		if os.path.exists(dt_path):
			import_file_by_path(dt_path, force=True)
			reinstalled.append(dt)

	if reinstalled:
		frappe.db.commit()  # setup: reimporta child tables ausentes após migrate
		frappe.logger().info("Reinstalados DocTypes: {0}".format(reinstalled))
