"""Preenche funded_by em Subcontract legados (padrão: Escritório)."""

import frappe

from engenharia.work_costs import FUNDED_BY_OFFICE


def execute():
	if not frappe.db.table_exists("tabSubcontract"):
		return
	if not frappe.db.has_column("Subcontract", "funded_by"):
		return

	frappe.db.sql(
		"""
		UPDATE `tabSubcontract`
		SET funded_by = %s
		WHERE IFNULL(funded_by, '') = ''
		""",
		(FUNDED_BY_OFFICE,),
	)
	frappe.db.commit()  # patch: backfill funded_by em Subcontract legado
