import frappe
from frappe import _
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
from frappe.utils import add_days, cint, today


def _app_display_name():
	return frappe.db.get_single_value("System Settings", "app_name") or "Engenharia"


def _default_notify_days():
	return cint(frappe.db.get_single_value("Engineering Settings", "default_notify_days")) or 3


def _manager_users():
	users = frappe.get_all(
		"Has Role",
		filters={"role": "Engenharia Manager", "parenttype": "User"},
		pluck="parent",
		limit_page_length=100,
	)
	return [u for u in users if u and u != "Administrator"] or ["Administrator"]


def _notification_already_sent(document_type, document_name, subject):
	return frappe.db.exists(
		"Notification Log",
		{
			"document_type": document_type,
			"document_name": document_name,
			"subject": subject,
		},
	)


def _send_system_notification(users, doctype, docname, subject, message):
	users = [u for u in (users or []) if u]
	if not users:
		users = ["Administrator"]
	enqueue_create_notification(
		users=users,
		doc={
			"type": "Alert",
			"document_type": doctype,
			"document_name": docname,
			"subject": subject,
			"email_content": message,
			"from_user": frappe.session.user or "Administrator",
		},
	)


def notify_deadlines_daily():
	"""E-mail diário com prazos vencidos ou dentro da janela de notificação."""
	hoje = today()
	default_days = _default_notify_days()

	deadlines = frappe.get_all(
		"Deadline",
		filters={"status": "Pendente"},
		fields=[
			"name",
			"project",
			"customer",
			"due_date",
			"description",
			"priority",
			"assigned_to",
			"notify_days_before",
		],
		limit_page_length=500,
	)

	urgent = []
	for row in deadlines:
		if not row.due_date:
			continue
		days_left = frappe.utils.date_diff(row.due_date, hoje)
		notify_days = row.notify_days_before or default_days
		if days_left <= notify_days:
			row["days_left"] = days_left
			urgent.append(row)

	if not urgent:
		return

	overdue = []
	upcoming = []
	for row in sorted(urgent, key=lambda x: x["days_left"]):
		if row["days_left"] < 0:
			overdue.append(row)
		else:
			upcoming.append(row)

	html = "<h3>{0} - {1}</h3>".format(
		_("Notificação de Prazos"),
		frappe.utils.escape_html(_app_display_name()),
	)

	if overdue:
		html += "<h4 style='color:red'>{0}</h4><ul>".format(_("Prazos vencidos"))
		for row in overdue:
			html += "<li><b>{0}</b> - venceu há {1} dia(s) - Obra: {2} - Cliente: {3}</li>".format(
				row.description or row.name,
				abs(row["days_left"]),
				row.project or "N/A",
				row.customer or "N/A",
			)
		html += "</ul>"

	if upcoming:
		html += "<h4 style='color:orange'>{0}</h4><ul>".format(_("Prazos próximos"))
		for row in upcoming:
			if row["days_left"] == 0:
				label = _("HOJE")
			elif row["days_left"] == 1:
				label = _("AMANHÃ")
			else:
				label = _("em {0} dias").format(row["days_left"])
			html += "<li><b>{0}</b> - vence {1} ({2}) - Obra: {3} - Cliente: {4}</li>".format(
				row.description or row.name,
				label,
				frappe.utils.formatdate(row.due_date, "dd/MM/yyyy"),
				row.project or "N/A",
				row.customer or "N/A",
			)
		html += "</ul>"

	html += "<p><a href='{0}/app/deadline?status=Pendente'>{1}</a></p>".format(
		frappe.utils.get_url(),
		_("Ver todos os prazos pendentes"),
	)

	recipients = _manager_users()
	frappe.sendmail(
		recipients=recipients,
		subject="[Engenharia] {0} prazo(s) urgente(s)".format(len(urgent)),
		message=html,
		now=True,
	)


def notify_expiring_permits():
	"""Notifica protocolos com validade nos próximos 30 dias."""
	hoje = today()
	limit = add_days(hoje, 30)
	permits = frappe.get_all(
		"Permit",
		filters={
			"status": ["in", ["Aprovado", "Em análise"]],
			"expiry_date": ["between", [hoje, limit]],
		},
		fields=["name", "project", "permit_type", "expiry_date", "owner"],
		limit_page_length=500,
	)

	count = 0
	for row in permits:
		subject = _("Protocolo expirando: {0}").format(row.name)
		if _notification_already_sent("Permit", row.name, subject):
			continue
		message = _(
			"O protocolo {0} ({1}) da obra {2} expira em {3}."
		).format(
			row.permit_type or row.name,
			row.name,
			row.project or _("N/A"),
			frappe.utils.formatdate(row.expiry_date),
		)
		_send_system_notification(
			users=[row.owner] if row.owner else _manager_users(),
			doctype="Permit",
			docname=row.name,
			subject=subject,
			message=message,
		)
		count += 1

	if count:
		frappe.logger().info("Notificações de protocolos expirando enviadas: {0}".format(count))


def notify_overdue_tasks():
	"""Notifica tarefas atrasadas (vencimento anterior a hoje)."""
	hoje = today()
	tasks = frappe.get_all(
		"Task",
		filters={
			"status": ["in", ["A fazer", "Fazendo"]],
			"due_date": ["<", hoje],
		},
		fields=["name", "subject", "project", "due_date", "assigned_to", "owner"],
		limit_page_length=500,
	)

	count = 0
	for row in tasks:
		subject = _("Tarefa atrasada: {0}").format(row.subject or row.name)
		if _notification_already_sent("Task", row.name, subject):
			continue
		message = _(
			"A tarefa {0} da obra {1} está atrasada (vencimento {2})."
		).format(
			row.subject or row.name,
			row.project or _("—"),
			frappe.utils.formatdate(row.due_date),
		)
		users = []
		if row.assigned_to:
			users.append(row.assigned_to)
		elif row.owner:
			users.append(row.owner)
		_send_system_notification(
			users=users,
			doctype="Task",
			docname=row.name,
			subject=subject,
			message=message,
		)
		count += 1

	if count:
		frappe.logger().info("Notificações de tarefas atrasadas enviadas: {0}".format(count))


def notify_overdue_payments():
	"""Notifica pagamentos vencidos há 3 dias."""
	target_date = add_days(today(), -3)
	payments = frappe.get_all(
		"Payment",
		filters={"status": "Vencido", "due_date": target_date},
		fields=["name", "title", "project", "customer", "due_date", "owner", "contract"],
		limit_page_length=500,
	)

	count = 0
	for row in payments:
		subject = _("Pagamento vencido: {0}").format(row.name)
		if _notification_already_sent("Payment", row.name, subject):
			continue
		origin = row.contract or row.project or _("N/A")
		message = _(
			"O pagamento {0} ({1}) venceu em {2}. Origem: {3}."
		).format(
			row.name,
			row.title or row.name,
			frappe.utils.formatdate(row.due_date),
			origin,
		)
		users = [row.owner] if row.owner else _manager_users()
		_send_system_notification(
			users=users,
			doctype="Payment",
			docname=row.name,
			subject=subject,
			message=message,
		)
		count += 1

	if count:
		frappe.logger().info("Notificações de pagamentos vencidos enviadas: {0}".format(count))
