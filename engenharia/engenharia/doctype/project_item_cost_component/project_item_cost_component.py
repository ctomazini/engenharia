from frappe.model.document import Document
from frappe.utils import flt


class ProjectItemCostComponent(Document):
	def validate(self):
		self.amount = flt(self.quantity) * flt(self.unit_cost)
