"""Helpers reutilizáveis para testes do app engenharia."""

import random

import frappe

from engenharia.validators import _calcular_dv_cnpj, _calcular_dv_cpf


def _uid(prefix="Teste"):
	return f"{prefix} {frappe.generate_hash(length=8)}"


def _gerar_cpf_valido():
	while True:
		base = "".join(str(random.randint(0, 9)) for _ in range(9))
		if len(set(base)) > 1:
			return base + _calcular_dv_cpf(base)


def _gerar_cnpj_valido():
	while True:
		base = "".join(str(random.randint(0, 9)) for _ in range(12))
		if len(set(base)) > 1:
			return base + _calcular_dv_cnpj(base)


def create_test_customer(person_type="Pessoa Física", customer_name=None, cpf=None, cnpj=None, **kwargs):
	if not customer_name:
		customer_name = _uid("Customer Teste")
	data = {
		"doctype": "Customer",
		"person_type": person_type,
		"customer_name": customer_name,
	}
	if person_type == "Pessoa Física":
		data["cpf"] = cpf if cpf is not None else _gerar_cpf_valido()
	else:
		data["cnpj"] = cnpj if cnpj is not None else _gerar_cnpj_valido()
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc
