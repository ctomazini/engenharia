import frappe
from frappe import _
from frappe.model.document import Document


class DocumentKit(Document):
	def validate(self):
		if not self.templates:
			frappe.throw(_("Informe ao menos um template no kit."), title=_("Kit inválido"))
