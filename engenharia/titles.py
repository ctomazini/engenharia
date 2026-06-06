"""Helpers para títulos no formato `{ID} — {descritor}`."""

import frappe

TITLE_SEPARATOR = " — "


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

	if doc.doctype == "Construction Measurement":
		period = (getattr(doc, "reference_period", None) or "").strip()
		if period:
			return period

	if doc.doctype == "Commission":
		supplier_name = (getattr(doc, "supplier_name", None) or "").strip()
		if supplier_name:
			return supplier_name

	if doc.doctype == "Project Stage":
		stage_type = getattr(doc, "stage_type", None)
		if stage_type:
			return stage_type

	if doc.doctype == "Time Log":
		activity = (getattr(doc, "activity", None) or "").strip()
		if activity:
			return activity

	if doc.doctype == "Communication Log":
		subject = (getattr(doc, "subject", None) or "").strip()
		if subject:
			return subject

	if doc.doctype == "Project Item":
		from engenharia.engenharia.doctype.project_item.project_item import build_project_item_descriptor

		descriptor = build_project_item_descriptor(doc)
		if descriptor:
			return descriptor

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
	"""Garante title no formato `{ID} — {descritor}`."""
	if doc.is_new() or not doc.name or str(doc.name).startswith("new-"):
		return
	descritor = _resolve_descriptor(doc, use_description=use_description)
	new_title = join_title_parts(doc.name, descritor)
	if new_title:
		doc.title = new_title
