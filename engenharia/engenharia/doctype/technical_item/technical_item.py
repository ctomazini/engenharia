import frappe
from frappe import _
from frappe.model.document import Document

from engenharia.formula_roles import VALID_OUTPUT_ROLES, VALUE_OUTPUT_ROLES
from engenharia.formulas import (
	build_formula_eval_context,
	formula_variable_names,
	safe_eval_formula,
	validate_formula_variables,
)
from engenharia.specifications import slugify_item_key, validate_field_key


class TechnicalItem(Document):
	def validate(self):
		self._normalize_item_key()
		self._validate_fields()
		self._validate_outputs()

	def _normalize_item_key(self):
		key = (self.item_key or "").strip()
		if not key:
			key = slugify_item_key(self.item_name)
		self.item_key = validate_field_key(key, title=_("Chave do item inválida"))

		duplicate = frappe.db.exists(
			"Technical Item",
			{"item_key": self.item_key, "name": ["!=", self.name]},
		)
		if duplicate:
			frappe.throw(
				_("Já existe item técnico com a chave {0}.").format(self.item_key),
				title=_("Chave duplicada"),
			)

	def _validate_fields(self):
		if not self.fields:
			frappe.throw(
				_("Defina ao menos um campo na tabela de especificação."),
				title=_("Template incompleto"),
			)

		seen_keys = set()
		for row in self.fields:
			field_key = validate_field_key(row.field_key, title=_("Campo inválido"))
			row.field_key = field_key
			if not (row.label or "").strip():
				frappe.throw(
					_("Rótulo obrigatório para o campo {0}.").format(field_key),
					title=_("Campo inválido"),
				)
			if field_key in seen_keys:
				frappe.throw(
					_("Chave de campo duplicada: {0}.").format(field_key),
					title=_("Campo inválido"),
				)
			seen_keys.add(field_key)

	def _validate_outputs(self):
		if not self.outputs:
			return

		field_keys = {row.field_key for row in self.fields}
		numeric_keys = {row.field_key for row in self.fields if row.data_type == "Número"}
		seen_output_keys: set[str] = set()
		declared_before: set[str] = set()
		value_role_count = 0

		for out in sorted(self.outputs, key=lambda row: row.sort_order or 0):
			label = (out.label or "").strip() or out.output_key or _("Saída")
			output_key = validate_field_key(out.output_key, title=_("Saída inválida"))
			out.output_key = output_key

			if not (out.label or "").strip():
				frappe.throw(
					_("Rótulo obrigatório para a saída {0}.").format(output_key),
					title=_("Saída inválida"),
				)
			role = (out.role or "").strip()
			if role and role not in VALID_OUTPUT_ROLES:
				frappe.throw(
					_("Papel inválido em {0}: {1}.").format(label, role),
					title=_("Saída inválida"),
				)
			out.role = role
			if role in VALUE_OUTPUT_ROLES:
				value_role_count += 1
				if value_role_count > 1:
					frappe.throw(
						_("Apenas uma saída pode ter o papel Valor total (value)."),
						title=_("Saída inválida"),
					)
			if output_key in field_keys:
				frappe.throw(
					_("A chave de saída {0} não pode ser igual a um campo de entrada.").format(output_key),
					title=_("Saída inválida"),
				)
			if output_key in seen_output_keys:
				frappe.throw(
					_("Chave de saída duplicada: {0}.").format(output_key),
					title=_("Saída inválida"),
				)
			seen_output_keys.add(output_key)

			formula = (out.formula or "").strip()
			if not formula:
				frappe.throw(
					_("Fórmula obrigatória para {0}.").format(label),
					title=_("Fórmula inválida"),
				)

			validate_formula_variables(
				formula,
				allowed_field_keys=numeric_keys,
				allowed_output_keys=declared_before,
				label=label,
			)

			ctx = build_formula_eval_context(
				numeric_field_keys=numeric_keys,
				output_keys_before=declared_before,
			)
			safe_eval_formula(formula, ctx)

			declared_before.add(output_key)
