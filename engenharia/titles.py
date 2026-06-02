"""Helpers para títulos no formato `{ID} — {descritor}`."""

import frappe

TITLE_SEPARATOR = " — "

COMPOSED = {
	"Construction Project": False,
	"Engineering Contract": False,
	"Payment": False,
	"Work Cost": True,
	"Reimbursable Expense": True,
}


def get_customer_name(customer):
	if not customer:
		return ""
	return frappe.db.get_value("Customer", customer, "customer_name") or customer


def join_title_parts(*parts):
	cleaned = [str(part).strip() for part in parts if part and str(part).strip()]
	return TITLE_SEPARATOR.join(cleaned)


def _resolve_descriptor(doc, use_description=False):
	if doc.doctype == "Construction Project":
		parts = []
		if doc.customer:
			parts.append(get_customer_name(doc.customer))
		if doc.city:
			parts.append(doc.city)
		if parts:
			return " - ".join(parts)

	if not use_description and getattr(doc, "customer", None):
		descritor = get_customer_name(doc.customer)
		if descritor:
			return descritor

	descritor = (getattr(doc, "description", None) or "").strip()
	if descritor:
		return descritor
	return doc.doctype


def apply_title_post_insert(doc, use_description=False):
	if not doc.name or str(doc.name).startswith("new-"):
		return
	current = (doc.title or "").strip()
	prefix = f"{doc.name}{TITLE_SEPARATOR}"
	if current.startswith(prefix):
		return
	if not current:
		descritor = _resolve_descriptor(doc, use_description=use_description)
	else:
		descritor = current
	new_title = join_title_parts(doc.name, descritor)
	if new_title:
		doc.db_set("title", new_title, update_modified=False)
		doc.title = new_title


def recompose_title(doc, use_description=False):
	"""Recompõe title no formato `{ID} — {descritor}`."""
	if doc.is_new() or not doc.name or str(doc.name).startswith("new-"):
		return
	descritor = _resolve_descriptor(doc, use_description=use_description)
	new_title = join_title_parts(doc.name, descritor)
	if new_title:
		doc.title = new_title


def recompose_title_if_empty(doc, use_description=False):
	if doc.is_new() or not doc.name or str(doc.name).startswith("new-"):
		return
	apply_title_post_insert(doc, use_description=use_description)
