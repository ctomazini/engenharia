import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, today

from engenharia.titles import apply_title_post_insert, recompose_title


class CommunicationLog(Document):
	def validate(self):
		if not self.communication_type:
			frappe.throw(_("Tipo é obrigatório."))
		if self.project and not self.customer:
			self.customer = frappe.db.get_value("Construction Project", self.project, "customer")
		self._compose_title()

	def after_insert(self):
		apply_title_post_insert(self)
		self._create_linked_task()

	def on_update(self):
		self._create_linked_task()

	def _compose_title(self):
		recompose_title(self)

	def _create_linked_task(self):
		"""Cria Tarefa de follow-up uma única vez, se solicitado."""
		if not self.create_task or not self.next_steps or self.task:
			return

		frappe.has_permission("Task", "create", throw=True)
		task = frappe.get_doc(
			{
				"doctype": "Task",
				"subject": f"Follow-up: {self.subject}",
				"description": self.next_steps,
				"project": self.project,
				"customer": self.customer,
				"status": "A fazer",
				"due_date": self.follow_up_date or add_days(today(), 3),
			}
		)
		task.insert()
		self.db_set("task", task.name)
