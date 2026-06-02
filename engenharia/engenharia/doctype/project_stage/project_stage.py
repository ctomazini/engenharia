import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class ProjectStage(Document):
	def validate(self):
		if flt(self.progress) < 0 or flt(self.progress) > 100:
			frappe.throw(_("Avanço deve estar entre 0 e 100."))
		if self.status == "Concluída" and flt(self.progress) < 100:
			self.progress = 100
		if self.status == "Não iniciada" and flt(self.progress) > 0:
			self.progress = 0
