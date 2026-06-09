import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, fmt_money, today

from engenharia.titles import apply_title_post_insert, recompose_title


class ReimbursableExpense(Document):
	def validate(self):
		if not self.is_new() and frappe.db.get_value(self.doctype, self.name, "status") == "Cancelado":
			frappe.throw(_("Despesa cancelada não pode ser alterada."))

		if not self.customer and self.project:
			self.customer = frappe.db.get_value("Construction Project", self.project, "customer")
		if not self.customer:
			frappe.throw(_("Cliente é obrigatório. Selecione uma Obra válida."))

		if flt(self.amount) <= 0:
			frappe.throw(_("Valor deve ser maior que zero."))

		self.compute_totals()
		if self.status != "Cancelado":
			self.update_reimbursement_status()

		self._compose_title()

	def after_insert(self):
		apply_title_post_insert(self, use_description=True)

	def compute_totals(self):
		self.total_office_paid = sum(flt(row.amount) for row in (self.office_payments or []))
		self.office_outstanding = flt(self.amount) - self.total_office_paid

		if self.total_office_paid > flt(self.amount):
			frappe.throw(
				_("Total pago pelo escritório ({0}) excede o valor da despesa ({1}).").format(
					fmt_money(self.total_office_paid),
					fmt_money(self.amount),
				)
			)

		if self.await_client_reimbursement:
			self.total_reimbursed = sum(flt(row.amount) for row in (self.reimbursements or []))
			self.reimbursement_outstanding = flt(self.amount) - self.total_reimbursed
			if self.total_reimbursed > flt(self.amount):
				frappe.throw(
					_("Total reembolsado ({0}) excede o valor da despesa ({1}).").format(
						fmt_money(self.total_reimbursed),
						fmt_money(self.amount),
					)
				)
		else:
			self.total_reimbursed = 0
			self.reimbursement_outstanding = 0

	def update_reimbursement_status(self):
		if self.status == "Cancelado":
			return

		if not self.await_client_reimbursement:
			self.status = "Reembolsado"
			self.client_reimbursed_date = None
			return

		if not self.reimbursements or self.total_reimbursed == 0:
			self.status = "A reembolsar"
			self.client_reimbursed_date = None
		elif self.total_reimbursed < flt(self.amount):
			self.status = "Parcialmente reembolsado"
			self.client_reimbursed_date = self._latest_reimbursement_date()
		else:
			self.status = "Reembolsado"
			self.client_reimbursed_date = self._latest_reimbursement_date()

	def _latest_reimbursement_date(self):
		dates = [row.payment_date for row in (self.reimbursements or []) if row.payment_date]
		return max(dates) if dates else today()

	def _compose_title(self):
		recompose_title(self, use_description=True)
