import frappe
from frappe import _
from frappe.model.document import Document
from frappe.query_builder.functions import Coalesce, Sum
from frappe.utils import flt, fmt_money

from engenharia.validators import validar_cnpj


def sync_project_commission_outstanding(project: str, exclude_name: str | None = None) -> None:
	if not project or not frappe.get_meta("Construction Project").has_field("commission_outstanding"):
		return

	commission = frappe.qb.DocType("Commission")
	query = (
		frappe.qb.from_(commission)
		.select(Coalesce(Sum(commission.outstanding), 0).as_("total"))
		.where(commission.construction_project == project)
		.where(commission.status != "Cancelled")
	)
	if exclude_name:
		query = query.where(commission.name != exclude_name)

	result = query.run(as_dict=True)
	total = flt(result[0].total if result else 0)

	frappe.db.set_value(
		"Construction Project",
		project,
		"commission_outstanding",
		total,
		update_modified=False,
	)


class Commission(Document):
	def validate(self):
		self._validate_supplier_tax_id()
		self._validate_total_value()
		self.compute_totals()
		self.update_status()
		self.compose_title()

	def on_update(self):
		sync_project_commission_outstanding(self.construction_project)

	def on_trash(self):
		sync_project_commission_outstanding(self.construction_project, exclude_name=self.name)

	def _validate_supplier_tax_id(self):
		if self.supplier_tax_id:
			self.supplier_tax_id = validar_cnpj(self.supplier_tax_id)

	def _validate_total_value(self):
		if flt(self.total_value) <= 0:
			frappe.throw(_("Valor total deve ser maior que zero."))

	def compute_totals(self):
		self.total_paid = sum(flt(row.amount) for row in (self.payments or []))
		self.outstanding = flt(self.total_value) - self.total_paid

		if self.total_paid > flt(self.total_value):
			frappe.throw(
				_("Total pago ({0}) excede o valor da comissão ({1}).").format(
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

	def compose_title(self):
		project_title = (
			frappe.db.get_value("Construction Project", self.construction_project, "title")
			or self.construction_project
		)
		self.title = f"{self.supplier_name} - {project_title}"
