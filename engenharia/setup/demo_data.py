"""Seeder reutilizável de dados de demonstração para o app engenharia."""

from __future__ import annotations

import os
import tempfile
from typing import Any

import frappe
from frappe.utils import flt, getdate, now_datetime, today

from engenharia.validators import _calcular_dv_cnpj, _calcular_dv_cpf

DEMO_MARKER = "_DEMO_"

CREATION_ORDER = [
	"Cost Category",
	"Stage Type",
	"Permit Type",
	"Public Agency",
	"Supplier",
	"Document Template",
	"Technical Item",
	"Customer",
	"Construction Project",
	"Project Stage",
	"Project Item",
	"Engineering Contract",
	"Commission",
	"Subcontract",
	"Work Cost",
	"Payment",
	"Reimbursable Expense",
	"Permit",
	"Deadline",
	"Task",
	"Construction Measurement",
	"Time Log",
	"Communication Log",
	"Document Kit",
]

# Campos usados para identificar registros transacionais no teardown
DEMO_MARKER_FIELDS: dict[str, str] = {
	"Customer": "customer_name",
	"Construction Project": "observations",
	"Engineering Contract": "observations",
	"Commission": "description",
	"Subcontract": "description",
	"Work Cost": "description",
	"Reimbursable Expense": "description",
	"Deadline": "description",
	"Task": "subject",
	"Time Log": "activity",
	"Communication Log": "subject",
}

# DocTypes vinculados a obras de demo (sem campo marcador próprio)
PROJECT_LINKED_DOCTYPES = (
	"Project Stage",
	"Project Item",
	"Construction Measurement",
	"Payment",
)

_refs: dict[str, Any] = {}


def setup() -> None:
	"""Popula dados de demo de forma idempotente."""
	teardown()
	_refs.clear()
	frappe.flags.in_demo_seed = True
	try:
		_seed_cost_categories()
		_seed_stage_types()
		_seed_permit_types()
		_seed_public_agencies()
		_seed_suppliers()
		_seed_document_templates()
		_seed_technical_items()
		_seed_customers()
		_seed_construction_projects()
		_seed_project_stages()
		_seed_project_items()
		_seed_engineering_contracts()
		_seed_commissions()
		_seed_subcontracts()
		_seed_work_costs()
		_seed_reimbursable_expenses()
		_seed_permits()
		_seed_deadlines()
		_seed_tasks()
		_seed_construction_measurements()
		_seed_time_logs()
		_seed_communication_logs()
		_seed_document_kits()
		verify()
	finally:
		frappe.flags.in_demo_seed = False


def teardown() -> None:
	"""Remove todos os dados de demonstração na ordem inversa."""
	frappe.flags.in_demo_teardown = True
	try:
		demo_projects = _get_demo_project_names()
		demo_customers = _get_demo_customer_names()

		for doctype in reversed(CREATION_ORDER):
			meta = frappe.get_meta(doctype)
			if meta.istable:
				continue

			names = _get_demo_doc_names(doctype, demo_projects, demo_customers)
			for name in names:
				try:
					frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)
				except Exception:
					frappe.log_error(title=f"Demo teardown: {doctype} {name}")
	finally:
		frappe.flags.in_demo_teardown = False


def verify() -> None:
	"""Verifica integridade mínima dos dados de demo."""
	errors: list[str] = []
	min_counts = {
		"Cost Category": 8,
		"Stage Type": 6,
		"Permit Type": 5,
		"Public Agency": 5,
		"Supplier": 6,
		"Subcontract": 2,
		"Technical Item": 5,
		"Customer": 6,
		"Construction Project": 6,
		"Engineering Contract": 4,
		"Commission": 3,
		"Work Cost": 6,
		"Reimbursable Expense": 3,
		"Permit": 5,
		"Deadline": 6,
		"Task": 5,
		"Time Log": 4,
		"Communication Log": 3,
	}

	for doctype, minimum in min_counts.items():
		count = _count_demo(doctype)
		if count < minimum:
			errors.append(f"❌ {doctype}: {count} registros (mínimo {minimum})")

	for key in ("p1", "p2", "p5"):
		project = _refs.get(f"project_{key}")
		if not project:
			continue
		total = flt(frappe.db.get_value("Construction Project", project, "spec_project_total"))
		items_sum = flt(
			frappe.db.sql(
				"""
				SELECT COALESCE(SUM(total_value), 0)
				FROM `tabProject Item`
				WHERE project = %s
				""",
				project,
			)[0][0]
		)
		if abs(total - items_sum) > 0.02:
			errors.append(
				f"❌ spec_project_total ({total}) != soma Project Items ({items_sum}) em {project}"
			)

	for cmsn_key in ("c1", "c2", "c3"):
		name = _refs.get(f"commission_{cmsn_key}")
		if not name:
			continue
		row = frappe.db.get_value(
			"Commission",
			name,
			["total_value", "total_paid", "outstanding"],
			as_dict=True,
		)
		if not row:
			continue
		expected = flt(row.total_value) - flt(row.total_paid)
		if abs(flt(row.outstanding) - expected) > 0.02:
			errors.append(f"❌ Commission {name}: outstanding inconsistente")

	for sub_key in ("s1", "s2"):
		name = _refs.get(f"subcontract_{sub_key}")
		if not name:
			continue
		row = frappe.db.get_value(
			"Subcontract",
			name,
			["total_value", "total_paid", "outstanding"],
			as_dict=True,
		)
		if not row:
			continue
		expected = flt(row.total_value) - flt(row.total_paid)
		if abs(flt(row.outstanding) - expected) > 0.02:
			errors.append(f"❌ Subcontract {name}: outstanding inconsistente")

	if errors:
		frappe.log_error("\n".join(errors), "Demo Data Verification Failed")
		print("\n".join(errors))
	else:
		print("✅ Todos os dados de demo verificados com sucesso.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _demo_name(label: str) -> str:
	return f"{DEMO_MARKER} {label}" if not label.startswith(DEMO_MARKER) else label


def _demo_cpf(seed: int) -> str:
	"""Gera CPF válido determinístico (evita sequências repetidas)."""
	digits = [((seed * 7 + i * 3) % 9) + 1 for i in range(9)]
	base = "".join(str(d) for d in digits)
	return base + _calcular_dv_cpf(base)


def _demo_cnpj(seed: int) -> str:
	"""Gera CNPJ válido determinístico (evita sequências repetidas)."""
	digits = [((seed * 11 + i * 5) % 9) + 1 for i in range(12)]
	base = "".join(str(d) for d in digits)
	return base + _calcular_dv_cnpj(base)


def _insert(doc_dict: dict) -> frappe.model.document.Document:
	doc = frappe.get_doc(doc_dict)
	doc.insert(ignore_permissions=True)  # setup: seed de dados de demonstração
	return doc


def _get_demo_project_names() -> list[str]:
	return frappe.get_all(
		"Construction Project",
		filters={"observations": ["like", f"%{DEMO_MARKER}%"]},
		pluck="name",
	)


def _get_demo_customer_names() -> list[str]:
	return frappe.get_all(
		"Customer",
		filters={"customer_name": ["like", f"{DEMO_MARKER}%"]},
		pluck="name",
	)


def _get_demo_doc_names(
	doctype: str,
	demo_projects: list[str] | None = None,
	demo_customers: list[str] | None = None,
) -> list[str]:
	meta = frappe.get_meta(doctype)
	if meta.autoname and meta.autoname.startswith("field:"):
		return frappe.get_all(doctype, filters={"name": ["like", f"{DEMO_MARKER}%"]}, pluck="name")

	if doctype in PROJECT_LINKED_DOCTYPES and demo_projects:
		return frappe.get_all(doctype, filters={"project": ["in", demo_projects]}, pluck="name")

	if doctype == "Payment" and demo_projects:
		return frappe.get_all(
			"Payment",
			filters={"project": ["in", demo_projects]},
			pluck="name",
		)

	marker_field = DEMO_MARKER_FIELDS.get(doctype)
	if marker_field:
		return frappe.get_all(
			doctype,
			filters={marker_field: ["like", f"%{DEMO_MARKER}%"]},
			pluck="name",
		)

	if doctype == "Permit" and demo_projects:
		return frappe.get_all(doctype, filters={"project": ["in", demo_projects]}, pluck="name")

	if doctype == "Commission" and demo_projects:
		return frappe.get_all(
			doctype,
			filters={"construction_project": ["in", demo_projects]},
			pluck="name",
		)

	if doctype == "Communication Log" and demo_customers:
		return frappe.get_all(
			doctype,
			filters={"customer": ["in", demo_customers], "subject": ["like", f"%{DEMO_MARKER}%"]},
			pluck="name",
		)

	return []


def _count_demo(doctype: str) -> int:
	meta = frappe.get_meta(doctype)
	if meta.istable:
		return 0
	if meta.autoname and meta.autoname.startswith("field:"):
		return frappe.db.count(doctype, {"name": ["like", f"{DEMO_MARKER}%"]})
	marker = DEMO_MARKER_FIELDS.get(doctype)
	if marker:
		return frappe.db.count(doctype, {marker: ["like", f"%{DEMO_MARKER}%"]})
	if doctype in PROJECT_LINKED_DOCTYPES or doctype in ("Permit", "Commission", "Payment"):
		projects = _get_demo_project_names()
		if not projects:
			return 0
		field = "project" if doctype != "Commission" else "construction_project"
		return frappe.db.count(doctype, {field: ["in", projects]})
	return 0


def _create_docx_file(paragraph: str = "Template demo {{ customer_name }}") -> str | None:
	try:
		from docx import Document as DocxDocument
	except ImportError:
		return None

	tmp_path = None
	try:
		with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
			tmp_path = tmp.name
			doc = DocxDocument()
			doc.add_paragraph(paragraph)
			doc.save(tmp_path)

		file_doc = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": f"demo_template_{frappe.generate_hash(length=6)}.docx",
				"is_private": 1,
			}
		)
		with open(tmp_path, "rb") as handle:
			file_doc.content = handle.read()
		file_doc.save(ignore_permissions=True)
		return file_doc.file_url
	finally:
		if tmp_path and os.path.exists(tmp_path):
			os.unlink(tmp_path)


def _create_project_item(
	project: str,
	technical_item: str,
	params: dict[str, float | int],
	instance_label: str | None = None,
) -> str:
	from engenharia.engenharia.doctype.project_item.project_item import (
		build_parameter_rows_from_template,
	)

	doc = frappe.new_doc("Project Item")
	doc.project = project
	doc.technical_item = technical_item
	doc.instance_label = instance_label or _demo_name("Item")
	doc.quantity = 1
	for row in build_parameter_rows_from_template(technical_item):
		key = row["field_key"]
		if key in params:
			row["value"] = str(params[key])
		doc.append("parameter_values", row)
	doc.insert(ignore_permissions=True)
	return doc.name


def _installment_row(due_date: str, amount: float, status: str, idx: int) -> dict:
	row = {
		"doctype": "Engineering Contract Installment",
		"due_date": due_date,
		"amount": flt(amount),
		"status": status,
		"description": f"{DEMO_MARKER} Parcela {idx}",
	}
	if status == "Recebido":
		row["received_amount"] = flt(amount)
		row["receipt_date"] = due_date
	return row


# ---------------------------------------------------------------------------
# Seeders
# ---------------------------------------------------------------------------


def _seed_cost_categories() -> None:
	names = [
		"Materiais",
		"Mão de Obra",
		"Equipamentos",
		"Transporte",
		"Alimentação",
		"Projetos e Consultoria",
		"Documentação e Taxas",
		"Outros",
	]
	for name in names:
		full = _demo_name(name)
		if frappe.db.exists("Cost Category", full):
			_refs[f"cost_{name}"] = full
			continue
		_insert({"doctype": "Cost Category", "category_name": full})
		_refs[f"cost_{name}"] = full


def _seed_stage_types() -> None:
	specs = [
		("Fundação", 1),
		("Estrutura", 2),
		("Alvenaria", 3),
		("Instalações", 4),
		("Acabamento", 5),
		("Entrega", 6),
	]
	for name, order in specs:
		full = _demo_name(name)
		if frappe.db.exists("Stage Type", full):
			_refs[f"stage_{name}"] = full
			continue
		_insert({"doctype": "Stage Type", "stage_name": full, "default_order": order})
		_refs[f"stage_{name}"] = full


def _seed_permit_types() -> None:
	names = [
		"Alvará de Construção",
		"Habite-se",
		"Licença Ambiental",
		"Aprovação de Projeto",
		"Licença de Demolição",
	]
	for name in names:
		full = _demo_name(name)
		if frappe.db.exists("Permit Type", full):
			_refs[f"permit_type_{name}"] = full
			continue
		_insert({"doctype": "Permit Type", "type_name": full, "is_art_rrt": 0})
		_refs[f"permit_type_{name}"] = full


def _seed_public_agencies() -> None:
	specs = [
		("Prefeitura Municipal de Novo Hamburgo", "Municipal", "Novo Hamburgo"),
		("Prefeitura Municipal de São Leopoldo", "Municipal", "São Leopoldo"),
		("CREA-RS", "Estadual", "Porto Alegre"),
		("IBAMA-RS", "Federal", "Porto Alegre"),
		("Corpo de Bombeiros - RS", "Estadual", "Porto Alegre"),
	]
	for name, sphere, city in specs:
		full = _demo_name(name)
		if frappe.db.exists("Public Agency", full):
			_refs[f"agency_{name}"] = full
			continue
		_insert(
			{
				"doctype": "Public Agency",
				"agency_name": full,
				"sphere": sphere,
				"city": city,
			}
		)
		_refs[f"agency_{name}"] = full


def _seed_suppliers() -> None:
	specs = [
		("Concreteira Vale dos Sinos Ltda", 1, "Material"),
		("Aço Forte Estruturas ME", 2, "Material"),
		("Elétrica Luminar Ltda", 3, "Material"),
		("Hidráulica Central EIRELI", 4, "Material"),
		("Pré-Moldados Gaúcho Ltda", 5, "Material"),
		("João Pedreiro ME", 6, "Mão de obra"),
	]
	for name, seed, category in specs:
		full = _demo_name(name)
		if frappe.db.exists("Supplier", full):
			_refs[f"supplier_{name}"] = full
			continue
		_insert(
			{
				"doctype": "Supplier",
				"supplier_name": full,
				"cnpj": _demo_cnpj(seed),
				"category": category,
				"phone": "5135885500",
				"email": f"contato{seed}@demo.example.com",
			}
		)
		_refs[f"supplier_{name}"] = full


def _seed_document_templates() -> None:
	specs = [
		("ART de Execução", "Relatório", "Template para ART de execução de obra"),
		("Contrato de Prestação de Serviço", "Contrato", "Template de contrato padrão"),
		("Laudo de Avaliação", "Relatório", "Template de laudo técnico imobiliário"),
	]
	file_url = _create_docx_file()
	if not file_url:
		frappe.log_error("python-docx não disponível — Document Templates/Kits omitidos no seed demo")
		return

	for name, doc_type, description in specs:
		full = _demo_name(name)
		if frappe.db.exists("Document Template", full):
			_refs[f"template_{name}"] = full
			continue
		_insert(
			{
				"doctype": "Document Template",
				"template_name": full,
				"document_type": doc_type,
				"description": description,
				"document_file": file_url,
				"enabled": 1,
			}
		)
		_refs[f"template_{name}"] = full


def _seed_technical_items() -> None:
	specs = [
		{
			"item_name": "Concreto Usinado FCK 30",
			"item_key": "demo_concreto_fck30",
			"category": "Estrutural",
			"default_unit": "m³",
			"fields": [
				{"field_key": "comprimento", "label": "Comprimento", "data_type": "Número", "sort_order": 1},
				{"field_key": "largura", "label": "Largura", "data_type": "Número", "sort_order": 2},
				{"field_key": "altura", "label": "Altura", "data_type": "Número", "sort_order": 3},
			],
			"outputs": [
				{
					"output_key": "volume",
					"label": "Volume",
					"formula": "comprimento * largura * altura",
					"sort_order": 1,
					"role": "volume",
					"unit": "m³",
				},
			],
		},
		{
			"item_name": "Alvenaria Bloco 14",
			"item_key": "demo_alvenaria_bloco14",
			"category": "Geral",
			"default_unit": "m²",
			"fields": [
				{"field_key": "comprimento", "label": "Comprimento", "data_type": "Número", "sort_order": 1},
				{"field_key": "altura", "label": "Altura", "data_type": "Número", "sort_order": 2},
				{"field_key": "desconto_vaos", "label": "Desconto Vãos", "data_type": "Número", "sort_order": 3},
			],
			"outputs": [
				{
					"output_key": "area_liquida",
					"label": "Área Líquida",
					"formula": "(comprimento * altura) - desconto_vaos",
					"sort_order": 1,
					"role": "area",
					"unit": "m²",
				},
			],
		},
		{
			"item_name": "Contrapiso",
			"item_key": "demo_contrapiso",
			"category": "Geral",
			"default_unit": "m²",
			"fields": [
				{"field_key": "comprimento", "label": "Comprimento", "data_type": "Número", "sort_order": 1},
				{"field_key": "largura", "label": "Largura", "data_type": "Número", "sort_order": 2},
			],
			"outputs": [
				{
					"output_key": "area",
					"label": "Área",
					"formula": "comprimento * largura",
					"sort_order": 1,
					"role": "area",
					"unit": "m²",
				},
			],
		},
		{
			"item_name": "Aço CA-50 10mm",
			"item_key": "demo_aco_ca50_10mm",
			"category": "Estrutural",
			"default_unit": "kg",
			"fields": [
				{"field_key": "comprimento_barra", "label": "Comprimento Barra", "data_type": "Número", "sort_order": 1},
				{"field_key": "qtd_barras", "label": "Quantidade Barras", "data_type": "Número", "sort_order": 2},
			],
			"outputs": [
				{
					"output_key": "peso_total",
					"label": "Peso Total",
					"formula": "comprimento_barra * qtd_barras * 0.617",
					"sort_order": 1,
					"role": "value",
					"unit": "kg",
				},
			],
		},
		{
			"item_name": "Eletroduto PVC 25mm",
			"item_key": "demo_eletroduto_pvc25",
			"category": "Elétrica",
			"default_unit": "m",
			"fields": [
				{"field_key": "comprimento", "label": "Comprimento", "data_type": "Número", "sort_order": 1},
				{"field_key": "quantidade", "label": "Quantidade", "data_type": "Número", "sort_order": 2},
			],
			"outputs": [
				{
					"output_key": "total_linear",
					"label": "Total Linear",
					"formula": "comprimento * quantidade",
					"sort_order": 1,
					"role": "value",
					"unit": "m",
				},
			],
		},
	]

	for spec in specs:
		full = _demo_name(spec["item_name"])
		if frappe.db.exists("Technical Item", full):
			_refs[f"ti_{spec['item_key']}"] = full
			continue
		doc = _insert(
			{
				"doctype": "Technical Item",
				"item_name": full,
				"item_key": spec["item_key"],
				"category": spec["category"],
				"data_type": "Número",
				"default_unit": spec["default_unit"],
				"fields": spec["fields"],
				"outputs": spec["outputs"],
			}
		)
		_refs[f"ti_{spec['item_key']}"] = doc.name


def _seed_customers() -> None:
	specs = [
		{
			"key": "joao",
			"name": "João Ricardo Ferreira",
			"person_type": "Pessoa Física",
			"cpf": _demo_cpf(1),
			"addresses": [
				{
					"street": "Rua das Acácias, 450",
					"city": "Novo Hamburgo",
					"state": "RS",
					"cep": "93510250",
				}
			],
			"contacts": [
				{
					"contact_name": "João Ricardo Ferreira",
					"mobile": "51999011234",
					"email": "joao.ferreira@email.com",
				}
			],
		},
		{
			"key": "maria",
			"name": "Maria Eduarda Gonçalves",
			"person_type": "Pessoa Física",
			"cpf": _demo_cpf(2),
			"addresses": [
				{
					"street": "Av. Pedro Adams Filho, 3100",
					"city": "Novo Hamburgo",
					"state": "RS",
					"cep": "93320001",
				}
			],
			"contacts": [
				{
					"contact_name": "Maria Eduarda Gonçalves",
					"mobile": "51998022345",
					"email": "maria.goncalves@email.com",
				}
			],
		},
		{
			"key": "horizonte",
			"name": "Construtora Horizonte Ltda",
			"person_type": "Pessoa Jurídica",
			"cnpj": _demo_cnpj(11),
			"addresses": [
				{
					"street": "Rua Joaquim Nabuco, 820",
					"city": "São Leopoldo",
					"state": "RS",
					"cep": "93020170",
				}
			],
			"contacts": [
				{
					"contact_name": "Contato Comercial",
					"phone": "5135885500",
					"email": "contato@horizonteconstrutora.com.br",
				}
			],
		},
		{
			"key": "pedro",
			"name": "Pedro Augusto da Silva",
			"person_type": "Pessoa Física",
			"cpf": _demo_cpf(3),
			"addresses": [
				{
					"street": "Rua General Osório, 155",
					"city": "Campo Bom",
					"state": "RS",
					"cep": "93700000",
				}
			],
			"contacts": [
				{
					"contact_name": "Pedro Augusto da Silva",
					"mobile": "51997033456",
					"email": "pedro.silva@email.com",
				}
			],
		},
		{
			"key": "sulgaucha",
			"name": "Incorporadora Sul Gaúcha S/A",
			"person_type": "Pessoa Jurídica",
			"cnpj": _demo_cnpj(22),
			"addresses": [
				{
					"street": "Av. Unisinos, 950, Sala 401",
					"city": "São Leopoldo",
					"state": "RS",
					"cep": "93022750",
				}
			],
			"contacts": [
				{
					"contact_name": "Projetos",
					"phone": "5135908800",
					"email": "projetos@sulgaucha.com.br",
				}
			],
		},
		{
			"key": "ana",
			"name": "Ana Cláudia Becker",
			"person_type": "Pessoa Física",
			"cpf": _demo_cpf(4),
			"addresses": [
				{
					"street": "Rua Tamandaré, 78",
					"city": "Estância Velha",
					"state": "RS",
					"cep": "93600000",
				}
			],
			"contacts": [
				{
					"contact_name": "Ana Cláudia Becker",
					"mobile": "51996044567",
					"email": "ana.becker@email.com",
				}
			],
		},
	]

	for spec in specs:
		full_name = _demo_name(spec["name"])
		existing = frappe.db.get_value("Customer", {"customer_name": full_name})
		if existing:
			_refs[f"customer_{spec['key']}"] = existing
			continue
		data: dict[str, Any] = {
			"doctype": "Customer",
			"customer_name": full_name,
			"person_type": spec["person_type"],
			"addresses": spec["addresses"],
			"contacts": spec["contacts"],
		}
		if spec["person_type"] == "Pessoa Física":
			data["cpf"] = spec["cpf"]
		else:
			data["cnpj"] = spec["cnpj"]
		doc = _insert(data)
		_refs[f"customer_{spec['key']}"] = doc.name


def _seed_construction_projects() -> None:
	specs = [
		{
			"key": "p1",
			"customer": "joao",
			"project_type": "Residencial",
			"observations": "Construção de residência unifamiliar 2 pavimentos",
			"city": "Novo Hamburgo",
			"address_uf": "RS",
			"status": "Em andamento",
			"construction_area": 180.50,
			"start_date": "2026-01-15",
			"expected_delivery": "2026-12-30",
			"address_street": "Rua das Acácias, 450 - Lote 12",
		},
		{
			"key": "p2",
			"customer": "horizonte",
			"project_type": "Industrial",
			"observations": "Galpão industrial pré-moldado 1200m²",
			"city": "São Leopoldo",
			"address_uf": "RS",
			"status": "Em andamento",
			"construction_area": 1200.00,
			"start_date": "2026-03-01",
			"expected_delivery": "2027-02-28",
			"address_street": "Distrito Industrial, Quadra 5, Lote 18",
		},
		{
			"key": "p3",
			"customer": "maria",
			"project_type": "Residencial",
			"observations": "Projeto arquitetônico e complementares - Sobrado",
			"city": "Novo Hamburgo",
			"address_uf": "RS",
			"status": "Em andamento",
			"construction_area": 220.00,
			"start_date": "2026-04-10",
			"expected_delivery": "2026-07-10",
			"address_street": "Av. Pedro Adams Filho, 3100",
		},
		{
			"key": "p4",
			"customer": "pedro",
			"project_type": "Outro",
			"observations": "Laudo técnico de avaliação imobiliária",
			"city": "Campo Bom",
			"address_uf": "RS",
			"status": "Concluída",
			"construction_area": 95.00,
			"start_date": "2025-11-01",
			"expected_delivery": "2025-12-15",
			"address_street": "Rua General Osório, 155",
		},
		{
			"key": "p5",
			"customer": "sulgaucha",
			"project_type": "Residencial",
			"observations": "Condomínio residencial 4 blocos - 48 unidades",
			"city": "São Leopoldo",
			"address_uf": "RS",
			"status": "Em andamento",
			"construction_area": 4800.00,
			"start_date": "2025-08-01",
			"expected_delivery": "2027-08-01",
			"address_street": "Av. Unisinos, lote 22-A",
		},
		{
			"key": "p6",
			"customer": "ana",
			"project_type": "Reforma",
			"observations": "Vistoria técnica para reforma de cobertura",
			"city": "Estância Velha",
			"address_uf": "RS",
			"status": "Concluída",
			"construction_area": 110.00,
			"start_date": "2026-05-01",
			"expected_delivery": "2026-05-15",
			"address_street": "Rua Tamandaré, 78",
		},
	]

	for spec in specs:
		marker_obs = f"{DEMO_MARKER} {spec['observations']}"
		existing = frappe.db.get_value("Construction Project", {"observations": marker_obs})
		if existing:
			_refs[f"project_{spec['key']}"] = existing
			continue
		doc = _insert(
			{
				"doctype": "Construction Project",
				"customer": _refs[f"customer_{spec['customer']}"],
				"project_type": spec["project_type"],
				"observations": marker_obs,
				"city": spec["city"],
				"address_uf": spec["address_uf"],
				"status": spec["status"],
				"construction_area": spec["construction_area"],
				"start_date": spec["start_date"],
				"expected_delivery": spec["expected_delivery"],
				"address_street": spec["address_street"],
			}
		)
		_refs[f"project_{spec['key']}"] = doc.name


def _seed_project_stages() -> None:
	plans = {
		"p1": [
			("Fundação", "Concluída", 100, 1),
			("Estrutura", "Em andamento", 45, 2),
			("Alvenaria", "Não iniciada", 0, 3),
		],
		"p2": [
			("Fundação", "Concluída", 100, 1),
			("Estrutura", "Concluída", 100, 2),
			("Alvenaria", "Em andamento", 30, 3),
			("Instalações", "Não iniciada", 0, 4),
			("Acabamento", "Não iniciada", 0, 5),
		],
		"p5": [
			("Fundação", "Concluída", 100, 1),
			("Estrutura", "Em andamento", 55, 2),
			("Alvenaria", "Não iniciada", 0, 3),
			("Instalações", "Não iniciada", 0, 4),
		],
	}
	stage_values = {"p1": 80000, "p2": 500000, "p5": 2000000}

	for proj_key, stages in plans.items():
		project = _refs[f"project_{proj_key}"]
		per_stage_value = flt(stage_values[proj_key]) / len(stages)
		for stage_name, status, progress, order in stages:
			stage_type = _refs[f"stage_{stage_name}"]
			_insert(
				{
					"doctype": "Project Stage",
					"project": project,
					"stage_type": stage_type,
					"status": status,
					"progress": progress,
					"order": order,
					"stage_value": per_stage_value,
				}
			)


def _seed_project_items() -> None:
	plans = {
		"p1": [
			("demo_concreto_fck30", {"comprimento": 10, "largura": 0.4, "altura": 0.6}),
			("demo_alvenaria_bloco14", {"comprimento": 45, "altura": 2.8, "desconto_vaos": 18}),
			("demo_contrapiso", {"comprimento": 12, "largura": 8}),
		],
		"p2": [
			("demo_concreto_fck30", {"comprimento": 40, "largura": 0.5, "altura": 0.8}),
			("demo_aco_ca50_10mm", {"comprimento_barra": 12, "qtd_barras": 200}),
			("demo_eletroduto_pvc25", {"comprimento": 6, "quantidade": 80}),
		],
		"p5": [
			("demo_concreto_fck30", {"comprimento": 60, "largura": 0.6, "altura": 1.0}),
			("demo_alvenaria_bloco14", {"comprimento": 320, "altura": 2.8, "desconto_vaos": 145}),
			("demo_aco_ca50_10mm", {"comprimento_barra": 12, "qtd_barras": 1500}),
			("demo_contrapiso", {"comprimento": 40, "largura": 30}),
		],
	}

	for proj_key, items in plans.items():
		project = _refs[f"project_{proj_key}"]
		for item_key, params in items:
			technical_item = _refs[f"ti_{item_key}"]
			_create_project_item(
				project,
				technical_item,
				params,
				instance_label=_demo_name(item_key),
			)


def _seed_engineering_contracts() -> None:
	contracts = [
		{
			"key": "cnt1",
			"project": "p1",
			"base_value": 320000.00,
			"first_installment_date": "2026-02-15",
			"installments": [
				("2026-02-15", 96000.00, "Recebido", 1),
				("2026-05-15", 96000.00, "Recebido", 2),
				("2026-08-15", 64000.00, "Pendente", 3),
				("2026-11-15", 64000.00, "Pendente", 4),
			],
		},
		{
			"key": "cnt2",
			"project": "p2",
			"base_value": 1850000.00,
			"first_installment_date": "2026-04-01",
			"installments": [
				("2026-04-01", 370000.00, "Recebido", 1),
				("2026-07-01", 370000.00, "Recebido", 2),
				("2026-10-01", 370000.00, "Pendente", 3),
				("2027-01-01", 370000.00, "Pendente", 4),
				("2027-02-28", 370000.00, "Pendente", 5),
			],
		},
		{
			"key": "cnt3",
			"project": "p3",
			"base_value": 45000.00,
			"first_installment_date": "2026-04-20",
			"installments": [
				("2026-04-20", 15000.00, "Recebido", 1),
				("2026-05-20", 15000.00, "Recebido", 2),
				("2026-07-10", 15000.00, "Pendente", 3),
			],
		},
		{
			"key": "cnt4",
			"project": "p5",
			"base_value": 5200000.00,
			"first_installment_date": "2025-09-01",
			"installments": [
				("2025-09-01", 520000.00, "Recebido", 1),
				("2025-12-01", 520000.00, "Recebido", 2),
				("2026-03-01", 520000.00, "Recebido", 3),
				("2026-06-01", 520000.00, "Pendente", 4),
				("2026-09-01", 520000.00, "Pendente", 5),
				("2026-12-01", 520000.00, "Pendente", 6),
				("2027-03-01", 520000.00, "Pendente", 7),
				("2027-06-01", 520000.00, "Pendente", 8),
				("2027-08-01", 520000.00, "Pendente", 9),
				("2027-08-01", 520000.00, "Pendente", 10),
			],
		},
	]

	for spec in contracts:
		project = _refs[f"project_{spec['project']}"]
		customer = frappe.db.get_value("Construction Project", project, "customer")
		rows = [
			_installment_row(due, amount, status, idx)
			for due, amount, status, idx in spec["installments"]
		]
		doc = _insert(
			{
				"doctype": "Engineering Contract",
				"project": project,
				"customer": customer,
				"base_value": spec["base_value"],
				"current_value": spec["base_value"],
				"installment_count": len(rows),
				"first_installment_date": spec["first_installment_date"],
				"observations": f"{DEMO_MARKER} Contrato de demonstração",
				"installments": rows,
			}
		)
		_refs[f"contract_{spec['key']}"] = doc.name
		# Re-save para disparar sync de Payment
		doc.reload()
		doc.save(ignore_permissions=True)


def _seed_commissions() -> None:
	supplier = _refs["supplier_Pré-Moldados Gaúcho Ltda"]
	supplier_cnpj = frappe.db.get_value("Supplier", supplier, "cnpj")
	specs = [
		{
			"key": "c1",
			"project": "p2",
			"commission_type": "Pré-Moldado",
			"total_value": 55000.00,
			"payments": [
				{"payment_date": "2026-05-10", "amount": 18000.00, "reference": "PIX-2026-0510"},
				{"payment_date": "2026-06-05", "amount": 18000.00, "reference": "PIX-2026-0605"},
			],
		},
		{
			"key": "c2",
			"project": "p5",
			"commission_type": "Pré-Moldado",
			"total_value": 120000.00,
			"payments": [
				{"payment_date": "2025-10-15", "amount": 30000.00, "reference": "TED-2025-1015"},
				{"payment_date": "2026-01-20", "amount": 30000.00, "reference": "TED-2026-0120"},
				{"payment_date": "2026-04-18", "amount": 30000.00, "reference": "PIX-2026-0418"},
			],
		},
		{
			"key": "c3",
			"project": "p4",
			"commission_type": "Outro",
			"total_value": 3000.00,
			"payments": [
				{"payment_date": "2025-12-20", "amount": 3000.00, "reference": "PIX-2025-1220"},
			],
		},
	]

	for spec in specs:
		doc = _insert(
			{
				"doctype": "Commission",
				"construction_project": _refs[f"project_{spec['project']}"],
				"commission_type": spec["commission_type"],
				"supplier_name": supplier,
				"supplier_tax_id": supplier_cnpj,
				"description": f"{DEMO_MARKER} Comissão de demonstração",
				"total_value": spec["total_value"],
				"payments": [
					{**p, "doctype": "Commission Payment"} for p in spec["payments"]
				],
			}
		)
		_refs[f"commission_{spec['key']}"] = doc.name


def _seed_subcontracts() -> None:
	mao_obra = _refs.get("cost_Mão de Obra") or _refs.get("cost_Mão de obra")
	if not mao_obra:
		mao_obra = frappe.db.get_value("Cost Category", {"category_name": ["like", f"%{DEMO_MARKER}%Mão%"]})
	specs = [
		{
			"key": "s1",
			"project": "p1",
			"supplier": "João Pedreiro ME",
			"total_value": 5000.00,
			"description": "Reboco e assentamento de blocos — área social",
			"payments": [
				{"payment_date": "2026-01-15", "amount": 2000.00, "payment_method": "PIX", "reference": "PIX-JAN"},
				{"payment_date": "2026-02-10", "amount": 3000.00, "payment_method": "TED", "reference": "TED-FEV"},
			],
		},
		{
			"key": "s2",
			"project": "p2",
			"supplier": "Concreteira Vale dos Sinos Ltda",
			"total_value": 12000.00,
			"description": "Equipe de concretagem — laje térreo",
			"payments": [
				{"payment_date": "2026-03-05", "amount": 4000.00, "payment_method": "PIX", "reference": "PIX-0305"},
			],
		},
	]

	for spec in specs:
		doc = _insert(
			{
				"doctype": "Subcontract",
				"project": _refs[f"project_{spec['project']}"],
				"supplier": _refs[f"supplier_{spec['supplier']}"],
				"cost_category": mao_obra,
				"description": f"{DEMO_MARKER} {spec['description']}",
				"total_value": spec["total_value"],
				"payments": [
					{**p, "doctype": "Subcontract Payment"} for p in spec["payments"]
				],
			}
		)
		_refs[f"subcontract_{spec['key']}"] = doc.name


def _seed_work_costs() -> None:
	specs = [
		("p1", "Materiais", "Cimento CP-II 50kg (40 sacos)", 1680.00),
		("p1", "Mão de Obra", "Servente - Março/2026", 1800.00),
		("p2", "Materiais", "Concreto usinado FCK30 - 1ª etapa (16m³)", 7200.00),
		("p2", "Equipamentos", "Locação betoneira 400L - 30 dias", 1800.00),
		("p5", "Materiais", "Aço CA-50 10mm - 1ª remessa", 48500.00),
		("p5", "Transporte", "Frete materiais São Paulo → São Leopoldo", 8200.00),
	]
	for proj_key, category, description, amount in specs:
		_insert(
			{
				"doctype": "Work Cost",
				"project": _refs[f"project_{proj_key}"],
				"cost_category": _refs[f"cost_{category}"],
				"description": f"{DEMO_MARKER} {description}",
				"amount": amount,
				"date": today(),
				"payments": [{"payment_date": today(), "amount": amount}],
			}
		)


def _seed_reimbursable_expenses() -> None:
	specs = [
		("p1", "Taxa de alvará de construção", 1250.00, "A reembolsar"),
		("p2", "ART de execução de obra", 180.00, "Reembolsado"),
		("p5", "Licença ambiental - estudo de impacto", 4500.00, "A reembolsar"),
	]
	for proj_key, description, amount, status in specs:
		data: dict[str, Any] = {
			"doctype": "Reimbursable Expense",
			"project": _refs[f"project_{proj_key}"],
			"description": f"{DEMO_MARKER} {description}",
			"amount": amount,
			"office_payments": [{"payment_date": today(), "amount": amount}],
		}
		if status == "Reembolsado":
			data["reimbursements"] = [{"payment_date": today(), "amount": amount}]
		_insert(data)


def _seed_permits() -> None:
	specs = [
		("p1", "Alvará de Construção", "Prefeitura Municipal de Novo Hamburgo", "AC-2026-0142", "Aprovado", "2026-01-10", "2027-01-10"),
		("p2", "Alvará de Construção", "Prefeitura Municipal de São Leopoldo", "AC-2026-0089", "Aprovado", "2026-02-20", "2027-02-20"),
		("p2", "Licença Ambiental", "IBAMA-RS", "LA-2026-00034", "Pendente", None, None),
		("p3", "Aprovação de Projeto", "Prefeitura Municipal de Novo Hamburgo", "AP-2026-0201", "Em análise", None, None),
		("p5", "Alvará de Construção", "Prefeitura Municipal de São Leopoldo", "AC-2025-0312", "Aprovado", "2025-07-15", "2027-07-15"),
	]
	for proj_key, permit_type, agency, number, status, protocol_date, expiry in specs:
		data: dict[str, Any] = {
			"doctype": "Permit",
			"project": _refs[f"project_{proj_key}"],
			"permit_type": _refs[f"permit_type_{permit_type}"],
			"public_agency": _refs[f"agency_{agency}"],
			"permit_number": number,
			"status": status,
		}
		if protocol_date:
			data["protocol_date"] = protocol_date
		if expiry:
			data["expiry_date"] = expiry
		_insert(data)


def _seed_deadlines() -> None:
	specs = [
		("p1", "Renovação do alvará de construção", "2027-01-10", "Pendente"),
		("p1", "Entrega do projeto estrutural revisado", "2026-06-15", "Pendente"),
		("p2", "Protocolo licença ambiental complementar", "2026-05-30", "Vencido"),
		("p2", "Entrega de laudo de sondagem", "2026-04-15", "Concluído"),
		("p5", "Vistoria do Corpo de Bombeiros", "2026-08-01", "Pendente"),
		("p5", "Renovação ART de execução", "2026-07-01", "Pendente"),
	]
	for proj_key, description, due_date, status in specs:
		_insert(
			{
				"doctype": "Deadline",
				"project": _refs[f"project_{proj_key}"],
				"description": f"{DEMO_MARKER} {description}",
				"due_date": due_date,
				"status": status,
				"deadline_type": "Projeto",
				"priority": "Média",
			}
		)


def _seed_tasks() -> None:
	specs = [
		("p1", "Solicitar orçamento de esquadrias de alumínio", "A fazer", "Média"),
		("p1", "Contratar topógrafo para levantamento", "Feito", "Alta"),
		("p2", "Revisar projeto de drenagem pluvial", "A fazer", "Alta"),
		("p5", "Agendar reunião com incorporadora - cronograma", "A fazer", "Alta"),
		("p5", "Solicitar ART complementar para fundações especiais", "A fazer", "Alta"),
	]
	for proj_key, subject, status, priority in specs:
		_insert(
			{
				"doctype": "Task",
				"project": _refs[f"project_{proj_key}"],
				"subject": f"{DEMO_MARKER} {subject}",
				"status": status,
				"priority": priority,
			}
		)


def _seed_construction_measurements() -> None:
	specs = [
		{
			"project": "p1",
			"reference_period": "Março/2026",
			"measurement_date": "2026-03-30",
			"items": [
				("Fundação", 85),
				("Estrutura", 40),
			],
		},
		{
			"project": "p2",
			"reference_period": "Abril/2026",
			"measurement_date": "2026-04-28",
			"items": [
				("Fundação", 100),
				("Estrutura", 95),
				("Alvenaria", 25),
			],
		},
		{
			"project": "p5",
			"reference_period": "Maio/2026",
			"measurement_date": "2026-05-30",
			"items": [
				("Fundação", 100),
				("Estrutura", 50),
			],
		},
	]

	for spec in specs:
		project = _refs[f"project_{spec['project']}"]
		items = []
		for stage_name, current_pct in spec["items"]:
			stage = frappe.db.get_value(
				"Project Stage",
				{"project": project, "stage_type": _refs[f"stage_{stage_name}"]},
			)
			items.append({"project_stage": stage, "current_pct": current_pct})

		_insert(
			{
				"doctype": "Construction Measurement",
				"project": project,
				"measurement_date": spec["measurement_date"],
				"reference_period": spec["reference_period"],
				"measurement_number": 1,
				"status": "Rascunho",
				"observations": f"{DEMO_MARKER} Medição de demonstração",
				"measurement_items": items,
			}
		)


def _seed_time_logs() -> None:
	specs = [
		("p1", "Acompanhamento de obra", "2026-06-02", 240),
		("p2", "Reunião com fornecedor", "2026-06-03", 120),
		("p3", "Elaboração de projeto", "2026-06-04", 360),
		("p5", "Vistoria de obra", "2026-06-05", 210),
	]
	for proj_key, activity, log_date, minutes in specs:
		_insert(
			{
				"doctype": "Time Log",
				"project": _refs[f"project_{proj_key}"],
				"activity": f"{DEMO_MARKER} {activity}",
				"log_date": log_date,
				"duration_minutes": minutes,
				"category": "Visita de Obra",
			}
		)


def _seed_communication_logs() -> None:
	specs = [
		("joao", "p1", "Telefone", "Alinhamento sobre cronograma da obra", "Cliente solicitou antecipação da etapa de acabamento."),
		("horizonte", "p2", "Email", "Envio de relatório de medição abril", "Enviado relatório de medição com planilha detalhada."),
		("sulgaucha", "p5", "Reunião Presencial", "Reunião de acompanhamento mensal", "Discutido atraso na entrega de aço e impacto no cronograma."),
	]
	for cust_key, proj_key, comm_type, subject, summary in specs:
		_insert(
			{
				"doctype": "Communication Log",
				"customer": _refs[f"customer_{cust_key}"],
				"project": _refs[f"project_{proj_key}"],
				"communication_date": now_datetime(),
				"communication_type": comm_type,
				"subject": f"{DEMO_MARKER} {subject}",
				"summary": summary,
			}
		)


def _seed_document_kits() -> None:
	if not _refs.get("template_ART de Execução"):
		return

	specs = [
		(
			"Kit Início de Obra",
			["ART de Execução", "Contrato de Prestação de Serviço"],
		),
		("Kit Laudo", ["Laudo de Avaliação"]),
	]
	for kit_name, templates in specs:
		full = _demo_name(kit_name)
		if frappe.db.exists("Document Kit", full):
			continue
		_insert(
			{
				"doctype": "Document Kit",
				"kit_name": full,
				"description": f"{DEMO_MARKER} Kit de documentos de demonstração",
				"enabled": 1,
				"templates": [
					{
						"doctype": "Document Kit Item",
						"document_template": _refs[f"template_{tpl}"],
						"sort_order": idx + 1,
					}
					for idx, tpl in enumerate(templates)
				],
			}
		)
