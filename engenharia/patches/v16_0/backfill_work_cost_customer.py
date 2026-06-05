"""Preenche customer em Work Cost legados a partir da obra."""

from __future__ import annotations

import frappe


def execute():
	if not frappe.db.table_exists("tabWork Cost"):
		return

	frappe.db.sql(
		"""
		UPDATE `tabWork Cost` wc
		INNER JOIN `tabConstruction Project` cp ON cp.name = wc.project
		SET wc.customer = cp.customer
		WHERE (wc.customer IS NULL OR wc.customer = '')
		  AND cp.customer IS NOT NULL
		  AND cp.customer != ''
		"""
	)
	frappe.db.commit()  # patch: backfill customer em Work Cost legado
