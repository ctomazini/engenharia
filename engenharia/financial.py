import frappe
from frappe import _
from frappe.utils import cstr, flt, now_datetime, today

# ── ignore_permissions justificativa ──────────────────────────────────
# Funções de sincronização rodam como doc_events disparados pelo save do
# usuário no Contrato/Pagamento. O sistema cria/atualiza Payments filho em
# nome do usuário autenticado. O acesso ao doc-pai já foi validado pelo
# Frappe antes do doc_event. ignore_permissions=True é intencional aqui.
# ──────────────────────────────────────────────────────────────────────

ORIGIN_CONTRACT_INSTALLMENT = "Parcela do Contrato"
ORIGIN_REIMBURSABLE = "Despesa Reembolsável"

STATUS_INSTALLMENT_TO_PAYMENT = {
	"Pendente": "Pendente",
	"Vencido": "Vencido",
	"Recebido": "Recebido",
	"Cancelado": "Cancelado",
}

STATUS_PAYMENT_TO_INSTALLMENT = {
	"Pendente": "Pendente",
	"Vencido": "Vencido",
	"Recebido": "Recebido",
	"Cancelado": "Cancelado",
	"Renegociado": "Pendente",
}

STATUS_EXPENSE_TO_PAYMENT = {
	"A reembolsar": "Pendente",
	"Parcialmente reembolsado": "Pendente",
	"Reembolsado": "Recebido",
	"Cancelado": "Cancelado",
}

STATUS_PAYMENT_TO_EXPENSE = {
	"Pendente": "A reembolsar",
	"Vencido": "A reembolsar",
	"Recebido": "Reembolsado",
	"Cancelado": "Cancelado",
}


def is_contract_installment_payment(payment) -> bool:
	origin = payment.get("origin_type") or ORIGIN_CONTRACT_INSTALLMENT
	return origin == ORIGIN_CONTRACT_INSTALLMENT


def is_reimbursable_payment(payment) -> bool:
	return (payment.get("origin_type") or "") == ORIGIN_REIMBURSABLE


def reimbursable_origin_id(expense_name: str) -> str:
	return f"REEMB-{expense_name}"


def sync_payments_hook(doc, method=None):
	if frappe.flags.in_payment_sync:
		return
	frappe.flags.in_payment_sync = True
	try:
		sync_payments_from_contract(doc)
	finally:
		frappe.flags.in_payment_sync = False


def sync_payments_from_contract(contract_doc, commit=False):
	"""Sincroniza parcelas do contrato com registros Payment (idempotente)."""
	contract = _as_contract_doc(contract_doc)
	if not contract or not contract.name:
		return {"created": 0, "updated": 0, "cancelled": 0}

	prev_flag = getattr(frappe.flags, "in_payment_sync", False)
	frappe.flags.in_payment_sync = True
	try:
		return _sync_payments_from_contract_impl(contract, commit)
	finally:
		frappe.flags.in_payment_sync = prev_flag


def _sync_payments_from_contract_impl(contract, commit=False):
	_ensure_installment_origin_ids(contract)
	installments = contract.get("installments") or []
	active_origin_ids = set()
	created = updated = cancelled = 0

	customer = contract.customer
	project = contract.project

	for idx, installment in enumerate(installments, start=1):
		origin_id = installment.installment_origin_id
		if not origin_id:
			continue
		active_origin_ids.add(origin_id)

		payment_name = frappe.db.get_value(
			"Payment", {"installment_origin_id": origin_id}, "name"
		)
		payload = _installment_to_payment_payload(contract, installment, idx, customer, project)

		if not payment_name:
			doc = frappe.get_doc({"doctype": "Payment", **payload})
			doc.insert(ignore_permissions=True)
			_link_payment_on_installment(origin_id, doc.name)
			created += 1
			continue

		payment = frappe.get_doc("Payment", payment_name)
		_link_payment_on_installment(origin_id, payment_name)
		if _can_update_payment(payment):
			changed = _apply_payment_payload(payment, payload)
			if changed:
				payment.save(ignore_permissions=True)
				updated += 1
		elif payment.status not in ("Recebido", "Cancelado"):
			_sync_status_from_installment(payment, installment)

	cancelled += _cancel_orphan_payments(contract.name, active_origin_ids)

	frappe.logger().info(
		"Sync pagamentos contrato {0}: +{1} ~{2} cancelados {3}".format(
			contract.name, created, updated, cancelled
		)
	)
	return {"created": created, "updated": updated, "cancelled": cancelled}


def sync_installment_from_payment(payment):
	"""Propaga status do Payment para a parcela contratual."""
	if not is_contract_installment_payment(payment):
		return
	if not payment.installment_origin_id:
		return

	installment_name = frappe.db.get_value(
		"Engineering Contract Installment",
		{"installment_origin_id": payment.installment_origin_id},
		"name",
	)
	if not installment_name:
		return

	updates = {}
	if payment.status == "Recebido":
		updates["status"] = "Recebido"
		updates["receipt_date"] = payment.received_date or today()
		updates["received_amount"] = payment.received_amount or payment.amount
	elif payment.status == "Vencido":
		updates["status"] = "Vencido"
	elif payment.status == "Cancelado":
		updates["status"] = "Cancelado"
	elif payment.status == "Pendente":
		updates["status"] = "Pendente"

	if payment.name:
		updates["payment"] = payment.name

	if updates:
		frappe.db.set_value(
			"Engineering Contract Installment",
			installment_name,
			updates,
			update_modified=True,
		)


def sync_payment_from_installment(installment):
	"""Propaga status da parcela contratual para o Payment vinculado."""
	if not installment.get("installment_origin_id"):
		return

	payment_name = frappe.db.get_value(
		"Payment", {"installment_origin_id": installment.installment_origin_id}, "name"
	)
	if not payment_name:
		return

	payment = frappe.get_doc("Payment", payment_name)
	if payment.status == "Cancelado":
		return
	if payment.manual_override or payment.status == "Recebido":
		_link_payment_on_installment(installment.installment_origin_id, payment_name)
		return

	new_status = STATUS_INSTALLMENT_TO_PAYMENT.get(installment.status or "Pendente", "Pendente")
	updates = {}
	if payment.status != new_status and payment.status in ("Pendente", "Vencido"):
		updates["status"] = new_status
	if installment.status == "Recebido" and installment.get("receipt_date"):
		if not payment.received_date:
			updates["received_date"] = installment.receipt_date
		if not payment.received_amount:
			updates["received_amount"] = installment.received_amount or installment.amount

	_link_payment_on_installment(installment.installment_origin_id, payment_name)

	if not updates:
		return

	already_syncing = getattr(frappe.flags, "in_payment_sync", False)
	if not already_syncing:
		frappe.flags.in_payment_sync = True
	try:
		updates["synced_at"] = now_datetime()
		frappe.db.set_value("Payment", payment_name, updates, update_modified=True)
	finally:
		if not already_syncing:
			frappe.flags.in_payment_sync = False


def _link_payment_on_installment(installment_origin_id, payment_name):
	if not installment_origin_id or not payment_name:
		return
	installment_name = frappe.db.get_value(
		"Engineering Contract Installment",
		{"installment_origin_id": installment_origin_id},
		"name",
	)
	if not installment_name:
		return
	current = frappe.db.get_value(
		"Engineering Contract Installment", installment_name, "payment"
	)
	if current != payment_name:
		frappe.db.set_value(
			"Engineering Contract Installment",
			installment_name,
			"payment",
			payment_name,
			update_modified=False,
		)


def _clear_installment_payment_link(payment):
	if not payment.name:
		return
	installments = frappe.get_all(
		"Engineering Contract Installment",
		filters={"payment": payment.name},
		pluck="name",
	)
	for installment_name in installments:
		frappe.db.set_value(
			"Engineering Contract Installment",
			installment_name,
			"payment",
			"",
			update_modified=False,
		)


def on_payment_trash(doc, method=None):
	if is_reimbursable_payment(doc):
		if doc.status == "Recebido":
			frappe.throw(
				_("Não é possível excluir Recebimento com status '{0}'. Cancele o recebimento primeiro.").format(
					doc.status
				),
				title=_("Exclusão Bloqueada"),
			)
		_clear_reimbursable_payment_link(doc)
		return

	if not is_contract_installment_payment(doc):
		return

	if doc.status == "Recebido":
		frappe.throw(
			_("Não é possível excluir Recebimento com status '{0}'. Cancele o recebimento primeiro.").format(
				doc.status
			),
			title=_("Exclusão Bloqueada"),
		)

	_clear_installment_payment_link(doc)


def process_payment_on_update(doc, method=None):
	"""Handler único de Payment.on_update."""
	from engenharia.tasks import on_payment_update

	on_payment_update(doc, method)
	on_payment_update_financial(doc, method)


def on_payment_update_financial(doc, method=None):
	if getattr(frappe.flags, "in_payment_sync", False):
		return
	if is_reimbursable_payment(doc):
		sync_reimbursable_from_payment(doc)
		return
	if not is_contract_installment_payment(doc):
		return

	sync_installment_from_payment(doc)

	if not doc.contract:
		return
	if doc.status == "Cancelado":
		verify_contract_settled(doc.contract)


def verify_contract_settled(contract_name):
	if not contract_name:
		return

	from engenharia.tasks import mark_contract_settled_if_complete

	contract_status = frappe.db.get_value("Engineering Contract", contract_name, "status")
	if contract_status == "Quitado":
		payments = frappe.get_all(
			"Payment",
			filters={
				"contract": contract_name,
				"origin_type": ["in", [ORIGIN_CONTRACT_INSTALLMENT, ""]],
				"status": ["not in", ["Cancelado"]],
			},
			fields=["status"],
		)
		if not payments or not all(p.status == "Recebido" for p in payments):
			frappe.db.set_value(
				"Engineering Contract",
				contract_name,
				"status",
				"Vigente",
				update_modified=True,
			)
			return

	mark_contract_settled_if_complete(contract_name, use_payments=True)


@frappe.whitelist()
def resync_contract_payments(contract_name: str) -> dict:
	contract = frappe.get_doc("Engineering Contract", contract_name)
	frappe.has_permission("Engineering Contract", "write", doc=contract, throw=True)
	sync_payments_from_contract(contract, commit=True)
	frappe.msgprint(
		_("Recebimentos re-sincronizados com sucesso."),
		title=_("Sincronização"),
		indicator="green",
	)
	return {"status": "ok"}


@frappe.whitelist()
def bulk_delete_payments(names: str | list):
	import json

	allowed_statuses = ("Pendente", "Cancelado")

	if isinstance(names, str):
		names = json.loads(names)
	if not names:
		frappe.throw(_("Nenhum recebimento selecionado."))
	frappe.has_permission("Payment", "delete", throw=True)

	deleted = []
	skipped = []

	for name in names:
		if not frappe.db.exists("Payment", name):
			skipped.append({"name": name, "reason": _("Registro não encontrado.")})
			continue

		doc = frappe.get_doc("Payment", name)
		if doc.status not in allowed_statuses:
			if doc.status == "Recebido":
				reason = _("Status '{0}' não permite exclusão em massa. Cancele primeiro.").format(
					doc.status
				)
			else:
				reason = _("Status '{0}' não permite exclusão em massa.").format(doc.status)
			skipped.append({"name": doc.name, "reason": reason})
			continue

		try:
			frappe.flags.in_bulk_delete = True
			frappe.delete_doc("Payment", doc.name, force=0, ignore_permissions=False)
			deleted.append(doc.name)
		except Exception as e:
			frappe.db.rollback()
			skipped.append({"name": doc.name, "reason": cstr(e)})

	return {"deleted": deleted, "skipped": skipped, "total": len(names)}


@frappe.whitelist()
def cancel_contract_payment(payment_name: str) -> dict:
	frappe.has_permission("Payment", "write", doc=payment_name, throw=True)

	payment = frappe.get_doc("Payment", payment_name)
	if not is_contract_installment_payment(payment):
		frappe.throw(_("Este recebimento não é de parcela de contrato."))

	if payment.status == "Cancelado":
		frappe.throw(_("Recebimento já está cancelado."))

	if payment.status == "Recebido":
		frappe.throw(
			_("Recebimento confirmado não pode ser cancelado."),
			title=_("Operação não permitida"),
		)

	payment.status = "Cancelado"
	payment.save(ignore_permissions=False)

	return {"success": True, "payment": payment.name, "contract": payment.contract}


def _as_contract_doc(contract_doc):
	if isinstance(contract_doc, str):
		return frappe.get_doc("Engineering Contract", contract_doc)
	if getattr(contract_doc, "doctype", None) == "Engineering Contract":
		return contract_doc
	return None


def _ensure_installment_origin_ids(contract):
	for installment in contract.get("installments") or []:
		if installment.installment_origin_id:
			continue
		new_id = _generate_installment_origin_id()
		installment.installment_origin_id = new_id
		if installment.name:
			frappe.db.set_value(
				"Engineering Contract Installment",
				installment.name,
				"installment_origin_id",
				new_id,
				update_modified=False,
			)


def _generate_installment_origin_id():
	return "INST-{0}".format(frappe.generate_hash(length=12))


def _installment_to_payment_payload(contract, installment, idx, customer, project):
	description = installment.get("description") or ""
	status = STATUS_INSTALLMENT_TO_PAYMENT.get(installment.status or "Pendente", "Pendente")
	received_amount = flt(installment.amount) if status == "Recebido" else 0

	return {
		"origin_type": ORIGIN_CONTRACT_INSTALLMENT,
		"contract": contract.name,
		"project": project,
		"customer": customer,
		"installment_origin_id": installment.installment_origin_id,
		"installment_number": idx,
		"description": description,
		"amount": flt(installment.amount),
		"received_amount": received_amount,
		"due_date": installment.due_date,
		"received_date": installment.receipt_date,
		"status": status,
		"notes": "",
		"synced_at": now_datetime(),
	}


def _can_update_payment(payment):
	if not is_contract_installment_payment(payment):
		return False
	if payment.status == "Cancelado":
		return False
	if payment.manual_override:
		return False
	if payment.status == "Recebido":
		return False
	if payment.received_date:
		return False
	return True


def _apply_payment_payload(payment, payload):
	changed = False
	for field in (
		"origin_type",
		"contract",
		"project",
		"customer",
		"installment_number",
		"description",
		"amount",
		"due_date",
		"notes",
	):
		if payment.get(field) != payload.get(field):
			payment.set(field, payload.get(field))
			changed = True
	if payment.status != payload.get("status") and payment.status in ("Pendente", "Vencido"):
		payment.status = payload.get("status")
		changed = True
	payment.synced_at = now_datetime()
	return changed


def _sync_status_from_installment(payment, installment):
	if payment.status == "Cancelado":
		return
	new_status = STATUS_INSTALLMENT_TO_PAYMENT.get(installment.status or "Pendente", "Pendente")
	if payment.status != new_status and payment.status in ("Pendente", "Vencido"):
		payment.status = new_status
		payment.synced_at = now_datetime()
		payment.save(ignore_permissions=True)


def _cancel_orphan_payments(contract_name, active_origin_ids):
	cancelled = 0
	filters = {
		"contract": contract_name,
		"origin_type": ["in", [ORIGIN_CONTRACT_INSTALLMENT, ""]],
	}
	if active_origin_ids:
		filters["installment_origin_id"] = ["not in", list(active_origin_ids)]

	orphans = frappe.get_all(
		"Payment",
		filters=filters,
		fields=["name", "status", "received_date", "installment_origin_id"],
	)
	for row in orphans:
		if row.status == "Recebido" or row.received_date:
			continue
		if row.status != "Cancelado":
			frappe.db.set_value(
				"Payment",
				row.name,
				{"status": "Cancelado", "synced_at": now_datetime()},
				update_modified=True,
			)
			cancelled += 1
	return cancelled


def sync_reimbursable_payments_hook(doc, method=None):
	if frappe.flags.in_payment_sync:
		return
	frappe.flags.in_payment_sync = True
	try:
		sync_payments_from_reimbursable(doc)
	finally:
		frappe.flags.in_payment_sync = False


def sync_payments_from_reimbursable(expense_doc):
	expense = _as_reimbursable_doc(expense_doc)
	if not expense or not expense.name:
		return

	origin_id = reimbursable_origin_id(expense.name)
	payment_name = frappe.db.get_value("Payment", {"installment_origin_id": origin_id}, "name")

	if not expense.await_client_reimbursement:
		if payment_name:
			payment = frappe.get_doc("Payment", payment_name)
			if payment.status not in ("Recebido", "Cancelado"):
				payment.status = "Cancelado"
				payment.save(ignore_permissions=True)
		return

	if expense.status == "Cancelado":
		if payment_name:
			payment = frappe.get_doc("Payment", payment_name)
			if payment.status != "Recebido":
				payment.status = "Cancelado"
				payment.save(ignore_permissions=True)
		return

	payload = _reimbursable_to_payment_payload(expense, origin_id)

	if not payment_name:
		doc = frappe.get_doc({"doctype": "Payment", **payload})
		doc.insert(ignore_permissions=True)
		_link_payment_on_reimbursable(expense.name, doc.name)
		return

	payment = frappe.get_doc("Payment", payment_name)
	_link_payment_on_reimbursable(expense.name, payment_name)
	if payment.status == "Cancelado":
		return
	if payment.manual_override or payment.status == "Recebido":
		return
	if _can_update_reimbursable_payment(payment):
		changed = _apply_reimbursable_payment_payload(payment, payload)
		if changed:
			payment.save(ignore_permissions=True)
	elif payment.status in ("Pendente", "Vencido"):
		new_status = payload.get("status")
		if new_status and payment.status != new_status:
			payment.status = new_status
			payment.synced_at = now_datetime()
			payment.save(ignore_permissions=True)


def sync_reimbursable_from_payment(payment):
	if not is_reimbursable_payment(payment):
		return
	if not payment.installment_origin_id or not payment.installment_origin_id.startswith("REEMB-"):
		return

	expense_name = payment.installment_origin_id.replace("REEMB-", "", 1)
	if not frappe.db.exists("Reimbursable Expense", expense_name):
		return

	expense = frappe.get_doc("Reimbursable Expense", expense_name)
	already_syncing = getattr(frappe.flags, "in_payment_sync", False)
	if not already_syncing:
		frappe.flags.in_payment_sync = True
	try:
		_sync_reimbursable_from_payment_impl(expense, payment)
	finally:
		if not already_syncing:
			frappe.flags.in_payment_sync = False


def _sync_reimbursable_from_payment_impl(expense, payment):
	updates = {}
	received_amount = flt(payment.received_amount or payment.amount)
	expense_amount = flt(expense.amount)

	if payment.status == "Recebido":
		if received_amount >= expense_amount:
			updates["status"] = "Reembolsado"
		elif received_amount > 0:
			updates["status"] = "Parcialmente reembolsado"
		else:
			updates["status"] = "Reembolsado"
		updates["client_reimbursed_date"] = payment.received_date or today()
		if received_amount > 0 and not expense.reimbursements:
			expense.append(
				"reimbursements",
				{
					"payment_date": payment.received_date or today(),
					"amount": received_amount,
					"reference": payment.name,
				},
			)
			expense.save(ignore_permissions=True)
			return
	elif payment.status == "Cancelado":
		updates["status"] = "Cancelado"
	elif payment.status in ("Pendente", "Vencido"):
		if expense.status != "Cancelado":
			if received_amount > 0 and received_amount < expense_amount:
				updates["status"] = "Parcialmente reembolsado"
			else:
				updates["status"] = "A reembolsar"
			if received_amount <= 0:
				updates["client_reimbursed_date"] = None

	if payment.name:
		updates["payment"] = payment.name

	if not updates:
		return

	for field, value in updates.items():
		expense.set(field, value)
	expense.save(ignore_permissions=True)


def _as_reimbursable_doc(expense_doc):
	if isinstance(expense_doc, str):
		return frappe.get_doc("Reimbursable Expense", expense_doc)
	if getattr(expense_doc, "doctype", None) == "Reimbursable Expense":
		return expense_doc
	return None


def _reimbursable_to_payment_payload(expense, origin_id):
	total_reimbursed = flt(expense.total_reimbursed)
	amount = flt(expense.amount)
	if expense.status == "Cancelado":
		status = "Cancelado"
	elif total_reimbursed >= amount and amount > 0:
		status = "Recebido"
	else:
		status = "Pendente"
	return {
		"origin_type": ORIGIN_REIMBURSABLE,
		"project": expense.project,
		"customer": expense.customer,
		"installment_origin_id": origin_id,
		"description": expense.description,
		"amount": amount,
		"received_amount": total_reimbursed,
		"due_date": expense.client_reimbursed_date or today(),
		"received_date": expense.client_reimbursed_date if total_reimbursed > 0 else None,
		"status": status,
		"notes": "",
		"synced_at": now_datetime(),
	}


def _can_update_reimbursable_payment(payment):
	if not is_reimbursable_payment(payment):
		return False
	if payment.status == "Cancelado":
		return False
	if payment.manual_override:
		return False
	if payment.status == "Recebido":
		return False
	if payment.received_date:
		return False
	return True


def _apply_reimbursable_payment_payload(payment, payload):
	changed = False
	for field in (
		"origin_type",
		"project",
		"customer",
		"description",
		"amount",
		"due_date",
		"notes",
	):
		if payment.get(field) != payload.get(field):
			payment.set(field, payload.get(field))
			changed = True
	if payment.status != payload.get("status") and payment.status in ("Pendente", "Vencido"):
		payment.status = payload.get("status")
		changed = True
	if payload.get("status") == "Recebido" or flt(payload.get("received_amount")) > 0:
		if payment.received_date != payload.get("received_date"):
			payment.received_date = payload.get("received_date")
			changed = True
		if flt(payment.received_amount) != flt(payload.get("received_amount")):
			payment.received_amount = payload.get("received_amount")
			changed = True
	payment.synced_at = now_datetime()
	return changed


def _link_payment_on_reimbursable(expense_name, payment_name):
	if not expense_name or not payment_name:
		return
	current = frappe.db.get_value("Reimbursable Expense", expense_name, "payment")
	if current != payment_name:
		frappe.db.set_value(
			"Reimbursable Expense",
			expense_name,
			"payment",
			payment_name,
			update_modified=False,
		)


def _clear_reimbursable_payment_link(payment):
	if not payment.name:
		return
	expenses = frappe.get_all(
		"Reimbursable Expense",
		filters={"payment": payment.name},
		pluck="name",
	)
	for expense_name in expenses:
		frappe.db.set_value(
			"Reimbursable Expense",
			expense_name,
			"payment",
			"",
			update_modified=False,
		)
