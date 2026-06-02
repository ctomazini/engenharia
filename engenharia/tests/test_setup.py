"""Helpers reutilizáveis para testes do app engenharia."""

import random

import frappe
from frappe.utils import add_months, flt, today

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


def create_test_construction_project(customer=None, **kwargs):
	if not customer:
		customer = create_test_customer().name
	data = {
		"doctype": "Construction Project",
		"customer": customer,
		"city": "São Paulo",
		"address_uf": "SP",
		"project_type": "Residencial",
		"status": "Orçamento",
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def _installment_row(due_date, amount, idx=1):
	return {
		"doctype": "Engineering Contract Installment",
		"due_date": due_date,
		"amount": flt(amount),
		"status": "Pendente",
		"description": f"Parcela {idx}",
	}


def create_test_engineering_contract(
	project=None,
	base_value=10000,
	installment_count=2,
	installments=None,
	**kwargs,
):
	if not project:
		project = create_test_construction_project().name
	customer = frappe.db.get_value("Construction Project", project, "customer")
	current_value = flt(kwargs.pop("current_value", base_value))

	if installments is None and installment_count:
		amount = current_value / installment_count
		installments = [
			_installment_row(add_months(today(), i), amount, i + 1)
			for i in range(installment_count)
		]

	doc = frappe.get_doc(
		{
			"doctype": "Engineering Contract",
			"project": project,
			"customer": customer,
			"base_value": base_value,
			"current_value": current_value,
			"installment_count": installment_count,
			"first_installment_date": today(),
			"installments": installments or [],
			**kwargs,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


def get_contract_payments(contract_name):
	return frappe.get_all(
		"Payment",
		filters={"contract": contract_name, "origin_type": "Parcela do Contrato"},
		fields=["name", "status", "installment_origin_id", "amount"],
		order_by="creation asc",
	)


def create_test_stage_type(stage_name=None, **kwargs):
	data = {
		"doctype": "Stage Type",
		"stage_name": stage_name or _uid("Etapa Tipo"),
		"default_order": 1,
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_project_stage(project=None, stage_type=None, **kwargs):
	if not project:
		project = create_test_construction_project().name
	if not stage_type:
		stage_type = create_test_stage_type().name
	data = {
		"doctype": "Project Stage",
		"project": project,
		"stage_type": stage_type,
		"status": "Não iniciada",
		"order": 1,
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_cost_category(category_name=None, **kwargs):
	data = {
		"doctype": "Cost Category",
		"category_name": category_name or _uid("Categoria"),
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_supplier(supplier_name=None, **kwargs):
	data = {
		"doctype": "Supplier",
		"supplier_name": supplier_name or _uid("Fornecedor"),
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_work_cost(project=None, amount=1000, **kwargs):
	if not project:
		project = create_test_construction_project().name
	data = {
		"doctype": "Work Cost",
		"project": project,
		"description": _uid("Custo"),
		"amount": amount,
		"status": "Pago",
		"date": today(),
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_reimbursable_expense(project=None, amount=500, **kwargs):
	if not project:
		project = create_test_construction_project().name
	data = {
		"doctype": "Reimbursable Expense",
		"project": project,
		"description": _uid("Despesa"),
		"amount": amount,
		"status": "A reembolsar",
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_task(project=None, subject=None, **kwargs):
	if not project:
		project = create_test_construction_project().name
	data = {
		"doctype": "Task",
		"project": project,
		"subject": subject or _uid("Tarefa"),
		"status": "A fazer",
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_public_agency(agency_name=None, **kwargs):
	data = {
		"doctype": "Public Agency",
		"agency_name": agency_name or _uid("Prefeitura"),
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_deadline(project=None, description=None, **kwargs):
	if not project:
		project = create_test_construction_project().name
	data = {
		"doctype": "Deadline",
		"project": project,
		"description": description or _uid("Prazo"),
		"due_date": today(),
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_communication_log(customer=None, project=None, **kwargs):
	if not customer and not project:
		project = create_test_construction_project().name
		customer = frappe.db.get_value("Construction Project", project, "customer")
	data = {
		"doctype": "Communication Log",
		"customer": customer,
		"project": project,
		"subject": _uid("Comunicação"),
		"communication_type": "Telefone",
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_time_log(project=None, activity=None, **kwargs):
	if not project:
		project = create_test_construction_project().name
	data = {
		"doctype": "Time Log",
		"project": project,
		"activity": activity or _uid("Atividade"),
		"log_date": today(),
		"duration_minutes": kwargs.pop("duration_minutes", 60),
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_permit(project=None, **kwargs):
	if not project:
		project = create_test_construction_project().name
	data = {
		"doctype": "Permit",
		"project": project,
		"permit_type": "Alvará",
		"protocol_date": today(),
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_payment(project=None, amount=1000, **kwargs):
	if not project:
		project = create_test_construction_project().name
	customer = frappe.db.get_value("Construction Project", project, "customer")
	data = {
		"doctype": "Payment",
		"project": project,
		"customer": customer,
		"amount": amount,
		"due_date": today(),
		"status": "Pendente",
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc
