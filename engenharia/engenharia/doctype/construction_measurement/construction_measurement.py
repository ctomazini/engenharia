import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from engenharia.titles import apply_title_post_insert, recompose_title


class ConstructionMeasurement(Document):
	def validate(self):
		if not self.customer and self.project:
			self.customer = frappe.db.get_value("Construction Project", self.project, "customer")
		if not self.customer:
			frappe.throw(_("Cliente é obrigatório. Selecione uma Obra válida."))

		if not self.measurement_items:
			frappe.throw(_("Informe ao menos um item de medição."))

		total = 0
		for row in self.measurement_items:
			self._validate_stage_belongs_to_project(row)
			self._compute_measurement_row(row)
			total += flt(row.measured_value)

		self.total_measured_value = total
		self._compose_title()

	def after_insert(self):
		apply_title_post_insert(self, use_description=True)

	def before_save(self):
		self._status_before_save = None if self.is_new() else frappe.db.get_value(self.doctype, self.name, "status")

	def on_update(self):
		if self.status != "Aprovada":
			return
		if not self.is_new() and self._status_before_save == "Aprovada":
			return
		self._apply_to_stages()

	def _validate_stage_belongs_to_project(self, row):
		if not row.project_stage:
			return

		stage_project = frappe.db.get_value("Project Stage", row.project_stage, "project")
		if stage_project and stage_project != self.project:
			frappe.throw(
				_("A etapa {0} não pertence à obra {1}.").format(row.project_stage, self.project),
				title=_("Etapa inválida"),
			)

	def _compute_measurement_row(self, row):
		if not row.project_stage:
			return

		stage = frappe.db.get_value(
			"Project Stage",
			row.project_stage,
			["progress", "stage_type", "stage_value"],
			as_dict=True,
		)
		if not stage:
			return

		row.previous_pct = flt(stage.progress)
		if not row.stage_description and stage.stage_type:
			row.stage_description = frappe.db.get_value("Stage Type", stage.stage_type, "stage_name") or stage.stage_type
		if not row.stage_value:
			row.stage_value = flt(stage.stage_value)

		current = flt(row.current_pct)
		if current < 0 or current > 100:
			frappe.throw(_("Percentual atual deve estar entre 0 e 100."))

		row.increment_pct = max(current - flt(row.previous_pct), 0)
		row.measured_value = flt(row.stage_value) * flt(row.increment_pct) / 100

	def _apply_to_stages(self):
		for row in self.measurement_items or []:
			if not row.project_stage:
				continue
			frappe.db.set_value(
				"Project Stage",
				row.project_stage,
				{"progress": flt(row.current_pct), "status": "Em andamento" if flt(row.current_pct) < 100 else "Concluída"},
				update_modified=True,
			)

		if self.project:
			from engenharia.project_progress import sync_project_physical_progress

			sync_project_physical_progress(self.project)

	def _compose_title(self):
		recompose_title(self, use_description=True)
