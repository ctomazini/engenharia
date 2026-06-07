import frappe
from frappe import _
from frappe.utils import add_days, today


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
		limit=500,
	)
	for row in payments:
		frappe.db.set_value("Payment", row.name, "status", "Vencido", update_modified=False)
		payment = frappe.get_doc("Payment", row.name)
		sync_installment_from_payment(payment)

	installments = frappe.get_all(
		"Engineering Contract Installment",
		filters={"due_date": ["<", hoje], "status": "Pendente"},
		pluck="name",
		limit=500,
	)
	for name in installments:
		frappe.db.set_value(
			"Engineering Contract Installment", name, "status", "Vencido", update_modified=False
		)


def check_overdue_reimbursable_expenses():
	"""Notifica despesas a reembolsar com pagamento antigo (60+ dias)."""
	from engenharia.notifications import _notification_already_sent, _send_system_notification

	cutoff = add_days(today(), -60)
	expenses = frappe.get_all(
		"Reimbursable Expense",
		filters={
			"status": "A reembolsar",
			"payment_date": ["<", cutoff],
		},
		fields=["name", "title", "project", "amount", "payment_date", "owner"],
		limit_page_length=500,
	)

	count = 0
	for row in expenses:
		subject = _("Despesa a reembolsar pendente: {0}").format(row.name)
		if _notification_already_sent("Reimbursable Expense", row.name, subject):
			continue
		message = _(
			"A despesa {0} ({1}) da obra {2} aguarda reembolso desde {3}."
		).format(
			row.title or row.name,
			frappe.utils.fmt_money(row.amount, currency="BRL"),
			row.project or _("N/A"),
			frappe.utils.formatdate(row.payment_date),
		)
		_send_system_notification(
			users=[row.owner] if row.owner else ["Administrator"],
			doctype="Reimbursable Expense",
			docname=row.name,
			subject=subject,
			message=message,
		)
		count += 1

	if count:
		frappe.logger().info("Notificações de reembolsáveis pendentes: {0}".format(count))


def check_project_status_weekly():
	"""Marca obras Em andamento como Concluída quando não há pendências operacionais."""
	hoje = today()

	projects = frappe.get_all(
		"Construction Project",
		filters={"status": "Em andamento"},
		pluck="name",
		limit_page_length=500,
	)
	if not projects:
		return

	contracts = frappe.get_all(
		"Engineering Contract",
		filters={"project": ["in", projects], "status": ["not in", ["Quitado", "Cancelado"]]},
		pluck="project",
		limit_page_length=500,
	)
	projects_with_open_contract = set(contracts)

	open_payments = frappe.get_all(
		"Payment",
		filters={
			"project": ["in", projects],
			"status": ["in", ["Pendente", "Vencido"]],
		},
		pluck="project",
		limit_page_length=500,
	)
	projects_with_open_payment = set(open_payments)

	open_deadlines = frappe.get_all(
		"Deadline",
		filters={"project": ["in", projects], "status": "Pendente"},
		pluck="project",
		limit_page_length=500,
	)
	projects_with_deadline = set(open_deadlines)

	open_tasks = frappe.get_all(
		"Task",
		filters={
			"project": ["in", projects],
			"status": ["in", ["A fazer", "Fazendo"]],
			"due_date": [">=", hoje],
		},
		pluck="project",
		limit_page_length=500,
	)
	projects_with_task = set(open_tasks)

	for name in projects:
		if name in projects_with_open_contract:
			continue
		if name in projects_with_open_payment:
			continue
		if name in projects_with_deadline:
			continue
		if name in projects_with_task:
			continue

		frappe.db.set_value(
			"Construction Project",
			name,
			"status",
			"Concluída",
			update_modified=True,
		)
		frappe.logger().info("Construction Project {0} marcada como Concluída".format(name))
