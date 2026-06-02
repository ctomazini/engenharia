import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class EngineeringContractInstallment(Document):
	def before_insert(self):
		if not self.installment_origin_id:
			self.installment_origin_id = "INST-{0}".format(frappe.generate_hash(length=12))

	def validate(self):
		if not self.is_new() and self.name:
			old_id = frappe.db.get_value(self.doctype, self.name, "installment_origin_id")
			if old_id and self.installment_origin_id and self.installment_origin_id != old_id:
				frappe.throw(_("ID de origem da parcela não pode ser alterado."))

	def before_save(self):
		self._update_status()

	def _update_status(self):
		if self.status == "Cancelado":
			return
		if self.receipt_date or (flt(self.received_amount) >= flt(self.amount) and flt(self.amount) > 0):
			self.status = "Recebido"
			if not self.receipt_date:
				self.receipt_date = today()
		elif self.due_date and str(self.due_date) < today():
			self.status = "Vencido"
		elif self.status != "Recebido":
			self.status = "Pendente"
