"""Renomeia colunas legadas de Reimbursable Expense antes do migrate."""

from __future__ import annotations

import frappe


def execute():
	if not frappe.db.table_exists("tabReimbursable Expense"):
		return

	if frappe.db.has_column("Reimbursable Expense", "reimburse_client") and not frappe.db.has_column(
		"Reimbursable Expense", "await_client_reimbursement"
	):
		frappe.rename_field("Reimbursable Expense", "reimburse_client", "await_client_reimbursement")

	if frappe.db.has_column("Reimbursable Expense", "reimbursement_date") and not frappe.db.has_column(
		"Reimbursable Expense", "client_reimbursed_date"
	):
		frappe.rename_field("Reimbursable Expense", "reimbursement_date", "client_reimbursed_date")
