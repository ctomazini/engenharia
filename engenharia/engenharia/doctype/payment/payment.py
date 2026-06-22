import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from engenharia.financial import ORIGIN_CONTRACT_INSTALLMENT, ORIGIN_REIMBURSABLE
from engenharia.titles import apply_title_post_insert, recompose_title


class Payment(Document):
	def validate(self):
		if not self.origin_type:
			self.origin_type = ORIGIN_CONTRACT_INSTALLMENT

		if self.project and not self.customer:
			self.customer = frappe.db.get_value("Construction Project", self.project, "customer")

		if self.origin_type == ORIGIN_CONTRACT_INSTALLMENT and not self.contract:
			frappe.throw(
				_("Contrato é obrigatório para recebimentos de parcela do contrato."),
				title=_("Campo obrigatório"),
			)

		if self.origin_type == ORIGIN_REIMBURSABLE and self.contract:
			frappe.throw(
				_("Recebimento de despesa reembolsável não pode estar vinculado a contrato."),
				title=_("Campo inválido"),
			)

		if flt(self.amount) < 0:
			frappe.throw(_("Valor não pode ser negativo."))

		if not self.is_new() and self.name:
			old_status = frappe.db.get_value(self.doctype, self.name, "status")
			if old_status == "Cancelado":
				frappe.throw(
					_("Recebimento cancelado não pode ser alterado. Exclua o registro se necessário."),
					title=_("Registro imutável"),
				)

		if self.installment_origin_id and not self.is_new():
			existing = frappe.db.get_value(
				"Payment",
				{"installment_origin_id": self.installment_origin_id, "name": ["!=", self.name]},
				"name",
			)
			if existing:
				frappe.throw(
					_("Já existe pagamento para a origem {0}.").format(self.installment_origin_id)
				)

		self._compose_title()

	def after_insert(self):
		apply_title_post_insert(self)

	def _compose_title(self):
		recompose_title(self)

	def before_save(self):
		if self.is_new() and self.status == "Cancelado":
			frappe.throw(_("Não é permitido criar pagamento já cancelado."))
