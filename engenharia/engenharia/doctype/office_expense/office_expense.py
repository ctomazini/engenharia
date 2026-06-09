import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, flt, getdate, today

from engenharia.titles import apply_title_post_insert, recompose_title


class OfficeExpense(Document):
	def validate(self):
		if flt(self.amount) <= 0:
			frappe.throw(_("Valor deve ser maior que zero."))

		self._compose_title()
		self._update_status()
		if self.is_recurring and self.due_date:
			self._calculate_next_due_date()

	def after_insert(self):
		apply_title_post_insert(self, use_description=True)

	def _compose_title(self):
		recompose_title(self, use_description=True)

	def _update_status(self):
		if self.status == "Cancelado":
			return
		if self.payment_date:
			self.status = "Pago"
		elif self.due_date and getdate(self.due_date) < getdate(today()):
			self.status = "Atrasado"
		elif not self.payment_date:
			self.status = "Pendente"

	def _calculate_next_due_date(self):
		months = {
			"Mensal": 1,
			"Bimestral": 2,
			"Trimestral": 3,
			"Semestral": 6,
			"Anual": 12,
		}
		if self.recurrence_frequency and self.recurrence_frequency in months:
			self.next_due_date = add_months(getdate(self.due_date), months[self.recurrence_frequency])


@frappe.whitelist()
def create_next_office_expense(source_name: str) -> str:
	"""Cria nova despesa recorrente com vencimento avançado."""
	frappe.has_permission("Office Expense", "create", throw=True)
	source = frappe.get_doc("Office Expense", source_name)
	if not source.is_recurring or not source.next_due_date:
		frappe.throw(_("Esta despesa não é recorrente ou não tem próximo vencimento calculado."))

	nova = frappe.copy_doc(source)
	nova.due_date = source.next_due_date
	nova.payment_date = None
	nova.status = "Pendente"
	nova.receipt = None
	nova.next_due_date = None
	nova.insert()
	return nova.name

