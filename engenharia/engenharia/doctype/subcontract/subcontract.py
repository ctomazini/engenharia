import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, fmt_money

from engenharia.titles import apply_title_post_insert, recompose_title


class Subcontract(Document):
	def validate(self):
		if not self.is_new() and frappe.db.get_value(self.doctype, self.name, "status") == "Cancelled":
			frappe.throw(_("Subcontrato cancelado não pode ser alterado."))

		if self.project and not self.customer:
			self.customer = frappe.db.get_value("Construction Project", self.project, "customer")

		self._validate_total_value()
		self.compute_totals()

		if self.status != "Cancelled":
			self.update_status()

		recompose_title(self)

	def after_insert(self):
		apply_title_post_insert(self)

	def _validate_total_value(self):
		if flt(self.total_value) <= 0:
			frappe.throw(_("Valor total deve ser maior que zero."))

	def compute_totals(self):
		self.total_paid = sum(flt(row.amount) for row in (self.payments or []))
		self.outstanding = flt(self.total_value) - self.total_paid

		if self.total_paid > flt(self.total_value):
			frappe.throw(
				_("Total pago ({0}) excede o valor acordado ({1}).").format(
					fmt_money(self.total_paid),
					fmt_money(self.total_value),
				)
			)

	def update_status(self):
		if self.status == "Cancelled":
			return

		if not self.payments or self.total_paid == 0:
			self.status = "Open"
		elif self.total_paid < flt(self.total_value):
			self.status = "Partially Paid"
		else:
			self.status = "Paid"
