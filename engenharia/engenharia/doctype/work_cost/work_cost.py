import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, fmt_money

from engenharia.titles import apply_title_post_insert, recompose_title
from engenharia.work_costs import FUNDED_BY_OFFICE


class WorkCost(Document):
	def validate(self):
		if not self.funded_by:
			self.funded_by = FUNDED_BY_OFFICE
		if not self.is_new() and frappe.db.get_value(self.doctype, self.name, "status") == "Cancelled":
			frappe.throw(_("Custo cancelado não pode ser alterado."))

		if flt(self.amount) <= 0:
			frappe.throw(_("Valor deve ser maior que zero."))

		if self.project and not self.customer:
			self.customer = frappe.db.get_value("Construction Project", self.project, "customer")

		self.compute_totals()
		if self.status != "Cancelled":
			self.update_status()

		self._compose_title()

	def after_insert(self):
		apply_title_post_insert(self, use_description=True)

	def compute_totals(self):
		self.total_paid = sum(flt(row.amount) for row in (self.payments or []))
		self.outstanding = flt(self.amount) - self.total_paid

		if self.total_paid > flt(self.amount):
			frappe.throw(
				_("Total pago ({0}) excede o valor acordado ({1}).").format(
					fmt_money(self.total_paid),
					fmt_money(self.amount),
				)
			)

	def update_status(self):
		if self.status == "Cancelled":
			return

		if not self.payments or self.total_paid == 0:
			self.status = "Open"
		elif self.total_paid < flt(self.amount):
			self.status = "Partially Paid"
		else:
			self.status = "Paid"

	def _compose_title(self):
		recompose_title(self, use_description=True)
