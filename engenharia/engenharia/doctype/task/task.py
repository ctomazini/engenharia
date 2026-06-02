import frappe
from frappe.model.document import Document
from frappe.utils import today


class Task(Document):
	def validate(self):
		if self.project and not self.customer:
			self.customer = frappe.db.get_value("Construction Project", self.project, "customer")

	def before_save(self):
		if self.status == "Feito" and not self.completed_on:
			self.completed_on = today()
		elif self.status != "Feito":
			self.completed_on = None

	@frappe.whitelist()
	def complete(self):
		self.check_permission("write")
		self.status = "Feito"
		self.completed_on = today()
		self.save()
		return {"status": self.status}
