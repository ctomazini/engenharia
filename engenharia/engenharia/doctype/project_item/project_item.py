import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, flt

from engenharia.formula_roles import TITLE_OUTPUT_ROLES, VALUE_OUTPUT_ROLES
from engenharia.formulas import build_formula_eval_context, safe_eval_formula, validate_parameter_row
from engenharia.project_rollup import on_project_item_change


def build_parameter_rows_from_template(technical_item: str) -> list[dict]:
	template = frappe.get_doc("Technical Item", technical_item)
	if not template.fields:
		frappe.throw(
			_("O item técnico {0} não possui campos no cadastro.").format(technical_item),
			title=_("Template incompleto"),
		)
	rows = []
	for field in sorted(template.fields, key=lambda row: row.sort_order or 0):
		rows.append(
			{
				"field_key": field.field_key,
				"label": field.label,
				"value": field.default_value or "",
				"unit": field.unit,
				"data_type": field.data_type,
				"required": field.required,
			}
		)
	return rows


@frappe.whitelist()
def get_parameter_template(technical_item: str) -> list[dict]:
	frappe.has_permission("Technical Item", "read", throw=True)
	return build_parameter_rows_from_template(technical_item)


class ProjectItem(Document):
	def validate(self):
		self.ensure_parameters_from_template()
		self.clean_incomplete_rows()
		self.validate_inputs()
		self.compute_outputs()
		self.compose_title()

	def after_insert(self):
		on_project_item_change(self)

	def on_update(self):
		on_project_item_change(self)

	def on_trash(self):
		on_project_item_change(self)

	def ensure_parameters_from_template(self) -> None:
		if not self.technical_item:
			return
		if self.parameter_values:
			return
		self.load_parameters_from_template()

	def load_parameters_from_template(self) -> None:
		self.set("parameter_values", [])
		for row in build_parameter_rows_from_template(self.technical_item):
			self.append("parameter_values", row)

	def clean_incomplete_rows(self) -> None:
		self.parameter_values = [
			row for row in (self.parameter_values or []) if (row.field_key or "").strip()
		]

	def validate_inputs(self) -> None:
		if not self.technical_item:
			frappe.throw(_("Item técnico é obrigatório."))

		if self.flags.get("ignore_required_parameters"):
			return

		if not self.parameter_values:
			frappe.throw(
				_("Nenhum parâmetro carregado. Escolha o item técnico ou use Recarregar parâmetros."),
				title=_("Parâmetros ausentes"),
			)

		instance = (self.instance_label or "").strip() or self.technical_item
		for row in self.parameter_values or []:
			validate_parameter_row(
				value=row.value,
				label=row.label or row.field_key,
				data_type=row.data_type or "Texto",
				required=bool(row.required),
				technical_item=self.technical_item,
				instance_label=instance,
			)

	def compute_outputs(self) -> None:
		template = frappe.get_doc("Technical Item", self.technical_item)
		numeric_values = {
			row.field_key: flt(row.value)
			for row in (self.parameter_values or [])
			if row.data_type == "Número" and cstr(row.value).strip()
		}

		ctx = build_formula_eval_context(
			numeric_field_keys=[f.field_key for f in template.fields if f.data_type == "Número"],
			parameter_values=numeric_values,
			quantity=self.quantity or 1,
		)

		self.set("computed_outputs", [])
		self.total_value = 0
		for out in sorted(template.outputs or [], key=lambda row: row.sort_order or 0):
			formula = (out.formula or "").strip()
			try:
				val = safe_eval_formula(formula, ctx)
			except frappe.ValidationError:
				raise
			except Exception:
				frappe.log_error(
					title=_("Erro na fórmula"),
					message=f"Formula {template.name}/{out.output_key}",
				)
				frappe.throw(_("Erro na fórmula de {0}").format(out.label))

			val = flt(val)
			ctx[out.output_key] = val
			role = (out.role or "").strip()
			self.append(
				"computed_outputs",
				{
					"output_key": out.output_key,
					"label": out.label,
					"role": role,
					"value": val,
					"unit": out.unit,
				},
			)
			if role in VALUE_OUTPUT_ROLES:
				self.total_value = val

	def compose_title(self) -> None:
		title_out = next(
			(o for o in (self.computed_outputs or []) if (o.role or "") in TITLE_OUTPUT_ROLES),
			None,
		)
		mult = "\u00d7"
		base = f"{self.technical_item} {mult}{self.quantity or 1}"
		if title_out and title_out.value is not None:
			unit = title_out.unit or ""
			self.title = f"{base} — {flt(title_out.value):.2f} {unit}".strip()
		else:
			instance = (self.instance_label or "").strip()
			self.title = f"{base} — {instance}" if instance else base
