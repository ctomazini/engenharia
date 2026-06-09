import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class ProjectStageTemplate(Document):
	def validate(self):
		self._validate_no_duplicate_stages()
		self._validate_total_weight()

	def _validate_no_duplicate_stages(self):
		if not self.stages:
			frappe.throw(_("Adicione pelo menos uma etapa ao template."))
		seen = set()
		for row in self.stages:
			if row.stage_type in seen:
				frappe.throw(_("Etapa {0} duplicada no template.").format(row.stage_type))
			seen.add(row.stage_type)

	def _validate_total_weight(self):
		total = sum(flt(row.weight) for row in self.stages)
		if abs(total - 100) > 0.01:
			frappe.throw(
				_("A soma dos pesos deve ser 100%. Atual: {0}%").format(round(total, 2))
			)
