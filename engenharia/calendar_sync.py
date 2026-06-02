import frappe


def sync_deadline_to_event(doc, method=None):
	"""Cria/atualiza Event do Frappe a partir de um Deadline."""
	if doc.status == "Concluído":
		_cancel_linked_event(doc)
		return

	event_name = _find_linked_event("Deadline", doc.name)

	event_data = {
		"subject": f"PRAZO: {doc.description}",
		"starts_on": doc.due_date,
		"all_day": 1,
		"event_type": "Public",
		"description": _deadline_description(doc),
		"color": _deadline_color(doc.priority),
		"custom_source_doctype": "Deadline",
		"custom_source_name": doc.name,
	}

	_save_or_create_event(event_name, event_data)


def sync_permit_to_event(doc, method=None):
	"""Cria/atualiza Event do Frappe a partir de um Permit."""
	if doc.status in ("Cancelado", "Indeferido"):
		_cancel_linked_event(doc)
		return

	event_date = doc.expiry_date or doc.protocol_date
	if not event_date:
		return

	event_name = _find_linked_event("Permit", doc.name)

	event_data = {
		"subject": f"PROTOCOLO: {doc.permit_type} — {doc.permit_number or doc.name}",
		"starts_on": event_date,
		"all_day": 1,
		"event_type": "Public",
		"description": _permit_description(doc),
		"color": _permit_color(doc.status),
		"custom_source_doctype": "Permit",
		"custom_source_name": doc.name,
	}

	_save_or_create_event(event_name, event_data)


def _find_linked_event(source_doctype, source_name):
	return frappe.db.get_value(
		"Event",
		{"custom_source_doctype": source_doctype, "custom_source_name": source_name},
	)


def _save_or_create_event(event_name, event_data):
	if event_name:
		event = frappe.get_doc("Event", event_name)
		event.update(event_data)
		event.save(ignore_permissions=True)  # sistema sincroniza Event em nome do usuário
	else:
		event = frappe.get_doc({"doctype": "Event", **event_data})
		event.insert(ignore_permissions=True)  # sistema sincroniza Event em nome do usuário


def _cancel_linked_event(doc):
	event_name = _find_linked_event(doc.doctype, doc.name)
	if event_name:
		frappe.db.set_value("Event", event_name, "status", "Closed")


def _deadline_color(priority):
	if priority == "Alta":
		return "red"
	if priority == "Média":
		return "orange"
	return "blue"


def _permit_color(status):
	if status == "Vencido":
		return "red"
	if status in ("Pendente", "Em análise"):
		return "orange"
	if status == "Aprovado":
		return "green"
	return "blue"


def _deadline_description(doc):
	parts = [f"Obra: {doc.project}", f"Prioridade: {doc.priority or 'Normal'}"]
	if doc.deadline_type:
		parts.append(f"Tipo: {doc.deadline_type}")
	if doc.public_agency:
		parts.append(f"Órgão: {doc.public_agency}")
	if doc.assigned_to:
		parts.append(f"Responsável: {doc.assigned_to}")
	if doc.notes:
		parts.append(f"Obs: {doc.notes}")
	return "\n".join(parts)


def _permit_description(doc):
	parts = [f"Obra: {doc.project}", f"Tipo: {doc.permit_type}", f"Status: {doc.status}"]
	if doc.public_agency:
		parts.append(f"Órgão: {doc.public_agency}")
	if doc.permit_number:
		parts.append(f"Protocolo: {doc.permit_number}")
	if doc.protocol_date:
		parts.append(f"Protocolo em: {doc.protocol_date}")
	if doc.expiry_date:
		parts.append(f"Validade: {doc.expiry_date}")
	return "\n".join(parts)
