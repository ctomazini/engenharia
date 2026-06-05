import frappe
from frappe import _
from frappe.model.document import Document


class ProjectSpecification(Document):
	def validate(self):
		frappe.throw(
			_("Project Specification foi substituído por Item do Projeto (Project Item)."),
			title=_("DocType legado"),
		)
