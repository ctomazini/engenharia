"""Preenche funded_by em Work Cost legados (padrão: Escritório)."""

import frappe

from engenharia.work_costs import FUNDED_BY_OFFICE


def execute():
	if not frappe.db.table_exists("tabWork Cost"):
		return
	if not frappe.db.has_column("Work Cost", "funded_by"):
		return

	frappe.db.sql(
		"""
		UPDATE `tabWork Cost`
		SET funded_by = %s
		WHERE IFNULL(funded_by, '') = ''
		""",
		(FUNDED_BY_OFFICE,),
	)
	frappe.db.commit()  # patch: backfill funded_by em Work Cost legado
