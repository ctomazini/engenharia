import frappe
from frappe.utils import today


def on_installment_update(doc, method=None):
	"""Propaga parcela → pagamento e marca contrato quitado quando aplicável."""
	from engenharia.financial import sync_payment_from_installment

	sync_payment_from_installment(doc)

	if doc.status != "Recebido":
		return
	if doc.parenttype != "Engineering Contract" or not doc.parent:
		return
	mark_contract_settled_if_complete(doc.parent)


def on_payment_update(doc, method=None):
	"""Propaga status do pagamento para contrato quitado."""
	if getattr(frappe.flags, "in_payment_sync", False):
		return

	if doc.status == "Cancelado":
		return

	if doc.status != "Recebido":
		return
	if not doc.contract:
		return
	mark_contract_settled_if_complete(doc.contract, use_payments=True)


def mark_contract_settled_if_complete(contract_name, use_payments=False):
	if use_payments:
		payments = frappe.get_all(
			"Payment",
			filters={"contract": contract_name, "status": ["not in", ["Cancelado"]]},
			fields=["status"],
		)
		if not payments or not all(p.status == "Recebido" for p in payments):
			return
	else:
		installments = frappe.get_all(
			"Engineering Contract Installment",
			filters={"parent": contract_name, "status": ["not in", ["Cancelado"]]},
			fields=["status"],
		)
		if not installments or not all(i.status == "Recebido" for i in installments):
			return

	current = frappe.db.get_value("Engineering Contract", contract_name, "status")
	if current != "Quitado":
		frappe.db.set_value(
			"Engineering Contract",
			contract_name,
			"status",
			"Quitado",
			update_modified=True,
		)


def check_overdue_installments():
	"""Marca pagamentos/parcelas pendentes vencidas como Vencido."""
	from engenharia.financial import sync_installment_from_payment

	hoje = today()

	payments = frappe.get_all(
		"Payment",
		filters={"due_date": ["<", hoje], "status": "Pendente", "manual_override": 0},
		fields=["name", "installment_origin_id"],
		limit_page_length=500,
	)
	for row in payments:
		frappe.db.set_value("Payment", row.name, "status", "Vencido", update_modified=False)
		payment = frappe.get_doc("Payment", row.name)
		sync_installment_from_payment(payment)

	installments = frappe.get_all(
		"Engineering Contract Installment",
		filters={"due_date": ["<", hoje], "status": "Pendente"},
		pluck="name",
		limit_page_length=500,
	)
	for name in installments:
		frappe.db.set_value(
			"Engineering Contract Installment", name, "status", "Vencido", update_modified=False
		)
