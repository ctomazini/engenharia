"""Sincroniza Payments para despesas reembolsáveis existentes."""

from __future__ import annotations

import frappe

from engenharia.financial import sync_payments_from_reimbursable


def execute():
	if not frappe.db.table_exists("tabReimbursable Expense"):
		return

	for name in frappe.get_all("Reimbursable Expense", pluck="name", limit_page_length=0):
		doc = frappe.get_doc("Reimbursable Expense", name)
		sync_payments_from_reimbursable(doc)

	frappe.db.commit()  # patch: cria/atualiza Payments de despesas reembolsáveis legadas
