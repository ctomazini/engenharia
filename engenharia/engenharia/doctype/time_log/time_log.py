import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_seconds

from engenharia.titles import apply_title_post_insert, recompose_title_if_empty


class TimeLog(Document):
	def validate(self):
		if not self.customer and self.project:
			self.customer = frappe.db.get_value("Construction Project", self.project, "customer")

		if self.duration_minutes is None:
			self.duration_minutes = 0

		if self.start_time and self.end_time and not self.duration_minutes:
			diff = time_diff_in_seconds(self.end_time, self.start_time)
			self.duration_minutes = max(0, int(diff / 60))

		self.duration_hours = round((self.duration_minutes or 0) / 60, 2)
		self._compose_title()

		if self.timer_active and self.has_value_changed("duration_minutes"):
			frappe.throw(
				_(
					"Não é possível editar a duração manualmente enquanto o timer está ativo. Pare o timer primeiro."
				)
			)

	def after_insert(self):
		apply_title_post_insert(self)

	def _compose_title(self):
		recompose_title_if_empty(self)

	@frappe.whitelist()
	def start_timer(self):
		self.check_permission("write")
		if self.timer_active:
			frappe.throw(_("Timer já está em execução para este registro."))

		self.timer_started_at = now_datetime()
		self.timer_active = 1
		self.save()

		return {"timer_started_at": str(self.timer_started_at)}

	@frappe.whitelist()
	def stop_timer(self):
		self.check_permission("write")
		if not self.timer_active:
			frappe.throw(_("Nenhum timer ativo para este registro."))

		elapsed_seconds = time_diff_in_seconds(now_datetime(), self.timer_started_at)
		elapsed_minutes = max(0, int(round(elapsed_seconds / 60)))

		current = self.duration_minutes or 0
		self.duration_minutes = current + elapsed_minutes
		self.duration_hours = round(self.duration_minutes / 60, 2)

		self.timer_started_at = None
		self.timer_active = 0
		self.save()

		return {
			"duration_minutes": self.duration_minutes,
			"duration_hours": self.duration_hours,
			"elapsed_seconds": elapsed_seconds,
		}


@frappe.whitelist()
def get_active_user_timer():
	"""Retorna o registro com timer ativo do usuário logado, se existir."""
	if frappe.session.user == "Guest":
		return None

	if not frappe.has_permission("Time Log", "read"):
		return None

	if not frappe.db.table_exists("Time Log"):
		return None

	user = frappe.session.user
	rows = frappe.get_all(
		"Time Log",
		filters={"timer_active": 1},
		fields=["name", "timer_started_at", "activity", "project", "assigned_to", "owner"],
		order_by="modified desc",
		limit=20,
	)

	for row in rows:
		if row.assigned_to and row.assigned_to != user:
			continue
		if not row.assigned_to and row.owner != user:
			continue
		return {
			"name": row.name,
			"timer_started_at": str(row.timer_started_at),
			"activity": row.activity or row.name,
			"project": row.project or "",
		}

	return None
