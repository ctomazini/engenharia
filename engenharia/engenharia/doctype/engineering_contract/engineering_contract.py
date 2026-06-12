import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, flt, getdate, today

from engenharia.titles import apply_title_post_insert, recompose_title


class EngineeringContract(Document):
	def validate(self):
		if not self.customer and self.project:
			self.customer = frappe.db.get_value("Construction Project", self.project, "customer")
		if not self.customer:
			frappe.throw(_("Cliente é obrigatório. Selecione uma Obra válida."))

		self._calculate_current_value()
		self._validate_financial()
		self._validate_installments()
		self._compose_title()

	def after_insert(self):
		apply_title_post_insert(self)

	def on_update(self):
		self._sync_project_contract_value()

	def on_trash(self):
		if self.project:
			sync_project_contract_value(self.project, exclude_contract=self.name)

	def _compose_title(self):
		recompose_title(self)

	def _calculate_current_value(self):
		base = flt(self.base_value)
		additions = sum(flt(row.amount) for row in self.amendments or [] if row.amendment_type == "Adição")
		reductions = sum(flt(row.amount) for row in self.amendments or [] if row.amendment_type == "Redução")
		self.current_value = base + additions - reductions

		count = flt(self.installment_count)
		if count > 0 and self.current_value > 0:
			self.installment_value = self.current_value / count

	def _validate_financial(self):
		if flt(self.base_value) < 0:
			frappe.throw(_("Valor base não pode ser negativo."))

		installments = self.get("installments") or []
		if installments and flt(self.current_value) <= 0:
			frappe.throw(_("Valor atual do contrato deve ser maior que zero."))

		if self.installment_count and flt(self.installment_count) > 0:
			has_fixed_date = any(
				(row.payment_condition or "Data fixa") == "Data fixa"
				for row in self.get("installments") or []
			)
			if has_fixed_date and not self.first_installment_date:
				frappe.throw(_("Informe a data da primeira parcela."))
			if flt(self.current_value) <= 0:
				frappe.throw(_("Valor atual deve ser maior que zero para gerar parcelas."))

	def _validate_installments(self):
		if frappe.flags.get("skip_installment_sum_validation"):
			return

		installments = [row for row in self.get("installments") or [] if row.status != "Cancelado"]
		if not installments:
			return

		total = sum(flt(row.amount) for row in installments)
		current = flt(self.current_value)
		diff = total - current

		if abs(diff) <= 0.02:
			return

		diff_label = frappe.format_value(diff, {"fieldtype": "Currency"})
		if diff > 0:
			detail = _("sobra de {0}").format(frappe.format_value(diff, {"fieldtype": "Currency"}))
		else:
			detail = _("falta de {0}").format(
				frappe.format_value(abs(diff), {"fieldtype": "Currency"})
			)

		frappe.throw(
			_("Soma das parcelas difere do total do contrato em {0} ({1}).").format(diff_label, detail),
			title=_("Erro de validação das parcelas"),
		)

		first_date = getdate(self.first_installment_date) if self.first_installment_date else None
		for row in installments:
			if first_date and row.due_date and getdate(row.due_date) < first_date:
				frappe.throw(
					_("Parcela {0}: vencimento anterior à data da primeira parcela.").format(row.idx)
				)

	def _sync_project_contract_value(self):
		if not self.project:
			return
		sync_project_contract_value(self.project)

	def regenerate_future_installments(self):
		received_rows = [row for row in self.installments or [] if row.status == "Recebido"]
		pending_rows = [
			row
			for row in self.installments or []
			if row.status not in ("Recebido", "Cancelado")
		]

		total_received = sum(flt(row.received_amount or row.amount) for row in received_rows)
		remaining = flt(self.current_value) - total_received
		if remaining < -0.02:
			frappe.throw(_("Valor recebido excede o valor atual do contrato após aditivo."))

		new_installments = list(received_rows)
		pending_count = len(pending_rows) or max(flt(self.installment_count), 1)

		if remaining > 0.02 and pending_count:
			amount_per = remaining / pending_count
			start_date = pending_rows[0].due_date if pending_rows else self.first_installment_date
			if not start_date:
				start_date = today()

			for index in range(int(pending_count)):
				new_installments.append(
					{
						"due_date": add_months(start_date, index),
						"amount": amount_per,
						"status": "Pendente",
						"description": _("Parcela {0}").format(len(received_rows) + index + 1),
					}
				)

		self.installments = []
		for row in new_installments:
			if isinstance(row, dict):
				self.append("installments", row)
			else:
				self.append(
					"installments",
					{
						"due_date": row.due_date,
						"amount": row.amount,
						"received_amount": row.received_amount,
						"receipt_date": row.receipt_date,
						"status": row.status,
						"description": row.description,
						"installment_origin_id": row.installment_origin_id,
						"payment": row.payment,
						"payment_condition": row.payment_condition,
					},
				)


def sync_project_contract_value(project, exclude_contract=None):
	"""Soma current_value de todos os contratos vigentes/quitados da obra."""
	if not project:
		return 0

	conditions = [
		"project = %s",
		"status IN ('Vigente', 'Quitado')",
	]
	params = [project]
	if exclude_contract:
		conditions.append("name != %s")
		params.append(exclude_contract)

	total = frappe.db.sql(
		f"""
		SELECT COALESCE(SUM(current_value), 0)
		FROM `tabEngineering Contract`
		WHERE {" AND ".join(conditions)}
		""",
		tuple(params),
	)[0][0]

	frappe.db.set_value(
		"Construction Project",
		project,
		"current_contract_value",
		flt(total),
		update_modified=False,
	)
	return flt(total)


@frappe.whitelist()
def apply_amendment(contract_name: str, regenerate: int = 0) -> dict:
	"""Aplica aditivos: opcionalmente regera parcelas futuras preservando recebidas."""
	contract = frappe.get_doc("Engineering Contract", contract_name)
	frappe.has_permission("Engineering Contract", "write", doc=contract, throw=True)

	if regenerate:
		contract.regenerate_future_installments()
		contract.save(ignore_permissions=True)  # whitelisted: write validado acima; save dispara sync
		message = _("Aditivo aplicado e parcelas futuras regeneradas.")
	else:
		frappe.flags.skip_installment_sum_validation = True
		try:
			contract.save(ignore_permissions=True)  # whitelisted: write validado acima; save dispara sync
		finally:
			frappe.flags.skip_installment_sum_validation = False
		message = _("Aditivo registrado no histórico.")

	frappe.msgprint(message, title=_("Aditivo"), indicator="green")
	return {"status": "ok", "regenerated": bool(regenerate)}
