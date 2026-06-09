"""Migra Reimbursable Expense legado para child tables de pagamento e reembolso."""

import frappe
from frappe.utils import flt, today


def execute():
	if not frappe.db.table_exists("tabReimbursable Expense"):
		return
	if not frappe.db.table_exists("tabReimbursable Expense Payment"):
		return

	meta = frappe.get_meta("Reimbursable Expense", cached=False)
	has_payment_date = meta.has_field("payment_date")

	for name in frappe.get_all("Reimbursable Expense", pluck="name", limit=0):
		doc = frappe.get_doc("Reimbursable Expense", name)
		payment_date = doc.get("payment_date") if has_payment_date else None

		if payment_date and flt(doc.amount) and not doc.office_payments:
			doc.append(
				"office_payments",
				{
					"payment_date": payment_date,
					"amount": flt(doc.amount),
				},
			)

		if doc.status == "Reembolsado" and doc.get("client_reimbursed_date") and not doc.reimbursements:
			doc.append(
				"reimbursements",
				{
					"payment_date": doc.client_reimbursed_date,
					"amount": flt(doc.amount),
				},
			)
		elif doc.status == "Reembolsado" and not doc.reimbursements and flt(doc.amount):
			doc.append(
				"reimbursements",
				{
					"payment_date": today(),
					"amount": flt(doc.amount),
				},
			)

		doc.compute_totals()
		if doc.status != "Cancelado":
			doc.update_reimbursement_status()
		doc.save(ignore_permissions=True)

	frappe.db.commit()  # patch: backfill pagamentos de Reimbursable Expense legado
