"""Validação e avaliação de fórmulas para itens técnicos e itens de obra."""

from __future__ import annotations

import ast
import math
from collections.abc import Iterable

import frappe
from frappe import _
from frappe.utils import cstr, flt

from engenharia.specifications import validate_field_key

FORMULA_BUILTIN_NAMES = frozenset({"pi", "sqrt", "quantity"})


def formula_variable_names(formula: str) -> set[str]:
	try:
		tree = ast.parse(cstr(formula).strip(), mode="eval")
	except SyntaxError as err:
		frappe.throw(
			_("Fórmula inválida: {0}").format(err),
			title=_("Fórmula inválida"),
		)
	names: set[str] = set()
	for node in ast.walk(tree):
		if isinstance(node, ast.Name):
			names.add(node.id)
	return names - FORMULA_BUILTIN_NAMES


def build_formula_eval_context(
	*,
	numeric_field_keys: Iterable[str],
	output_keys_before: Iterable[str] | None = None,
	parameter_values: dict[str, float] | None = None,
	quantity: float = 1,
) -> dict:
	ctx: dict = {
		"pi": math.pi,
		"sqrt": math.sqrt,
		"quantity": flt(quantity) or 1,
	}
	for key in numeric_field_keys:
		if parameter_values is not None:
			ctx[key] = flt(parameter_values.get(key))
		else:
			ctx[key] = 1
	for key in output_keys_before or ():
		if parameter_values is not None and key in parameter_values:
			ctx[key] = flt(parameter_values[key])
		else:
			ctx[key] = 1
	return ctx


def safe_eval_formula(formula: str, ctx: dict):
	formula = cstr(formula).strip()
	if not formula:
		frappe.throw(_("Fórmula vazia."), title=_("Fórmula inválida"))
	try:
		return frappe.safe_eval(formula, eval_locals=ctx)
	except SyntaxError as err:
		frappe.throw(
			_("Fórmula inválida: {0}").format(err),
			title=_("Fórmula inválida"),
		)
	except Exception as err:
		frappe.throw(
			_("Fórmula inválida: {0}").format(err),
			title=_("Fórmula inválida"),
		)


def validate_formula_variables(
	formula: str,
	*,
	allowed_field_keys: set[str],
	allowed_output_keys: set[str],
	label: str,
) -> None:
	unknown = formula_variable_names(formula) - allowed_field_keys - allowed_output_keys
	if unknown:
		frappe.throw(
			_("Fórmula em {0} referencia variável não permitida: {1}.").format(
				label,
				", ".join(sorted(unknown)),
			),
			title=_("Fórmula inválida"),
		)


def validate_parameter_row(
	*,
	value: str,
	label: str,
	data_type: str,
	required: bool,
	technical_item: str,
	instance_label: str | None = None,
) -> None:
	value = cstr(value).strip()
	if required and not value:
		suffix = f" ({instance_label})" if instance_label else ""
		frappe.throw(
			_("{0} é obrigatório em {1}{2}.").format(label, technical_item, suffix),
			title=_("Campo obrigatório"),
		)
	if not value:
		return
	if data_type == "Número":
		try:
			flt(value)
		except TypeError, ValueError:
			frappe.throw(
				_("{0} deve ser numérico.").format(label),
				title=_("Valor inválido"),
			)
	elif data_type == "Sim-Não" and value not in ("Sim", "Não"):
		frappe.throw(
			_("{0} deve ser Sim ou Não.").format(label),
			title=_("Valor inválido"),
		)
