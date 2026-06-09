"""Migra Work Cost legado (Pago/Pendente/Cancelado) para child table de pagamentos."""

import frappe
from frappe.utils import flt, today


def execute():
	if not frappe.db.table_exists("tabWork Cost"):
		return
	if not frappe.db.table_exists("tabWork Cost Payment"):
		return

	for name in frappe.get_all("Work Cost", pluck="name", limit=0):
		doc = frappe.get_doc("Work Cost", name)
		legacy_status = doc.status or "Open"

		if legacy_status in ("Pago", "Paid") and not doc.payments:
			doc.append(
				"payments",
				{
					"payment_date": doc.get("date") or today(),
					"amount": flt(doc.amount),
					"payment_method": doc.get("payment_method"),
				},
			)
			doc.status = "Paid"
		elif legacy_status in ("Pendente", "Open"):
			doc.status = "Open"
		elif legacy_status in ("Cancelado", "Cancelled"):
			doc.status = "Cancelled"

		doc.compute_totals()
		if doc.status not in ("Cancelled",):
			doc.update_status()
		doc.save(ignore_permissions=True)

	frappe.db.commit()  # patch: backfill pagamentos de Work Cost legado
