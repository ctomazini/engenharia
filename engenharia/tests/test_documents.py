import json
import os
import tempfile

import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.documents import (
	_build_context,
	generate_project_documents,
	get_available_kits,
	get_available_templates,
	get_document_placeholder_keys,
	get_placeholder_reference,
)
from engenharia.tests.test_setup import (
	_uid,
	create_test_construction_project,
	create_test_customer,
	create_test_engineering_contract,
	create_test_supplier,
)
from engenharia.tests.test_subcontract import create_test_subcontract


def _ensure_engineering_settings(company_name="Escritório Teste Engenharia"):
	settings = frappe.get_single("Engineering Settings")
	settings.company_name = company_name
	settings.company_cnpj = "11222333000181"
	settings.company_crea = "123456/D-SP"
	settings.bank_name = "Banco Teste"
	settings.bank_agency = "0001"
	settings.bank_account = "12345-6"
	settings.bank_pix = "teste@example.com"
	settings.save(ignore_permissions=True)
	return settings


def _create_test_document_template(paragraph="Doc test {{ customer_name }}"):
	try:
		from docx import Document as DocxDocument
	except ImportError:
		return None

	with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
		doc = DocxDocument()
		doc.add_paragraph(paragraph)
		doc.save(tmp.name)
		tmp_path = tmp.name

	try:
		file_doc = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": f"template_{frappe.generate_hash(length=6)}.docx",
				"is_private": 1,
			}
		)
		with open(tmp_path, "rb") as handle:
			file_doc.content = handle.read()
		file_doc.save(ignore_permissions=True)

		template = frappe.get_doc(
			{
				"doctype": "Document Template",
				"template_name": _uid("Template Doc"),
				"document_type": "Contrato",
				"document_file": file_doc.file_url,
				"enabled": 1,
			}
		).insert(ignore_permissions=True)
		return template.name
	finally:
		if os.path.exists(tmp_path):
			os.unlink(tmp_path)


VALID_FIXO = "1132345678"
VALID_CELULAR = "11987654321"


class TestDocuments(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_get_available_templates_list(self):
		result = get_available_templates()
		self.assertIsInstance(result, list)

	def test_get_available_kits_list(self):
		result = get_available_kits()
		self.assertIsInstance(result, list)

	def test_get_placeholder_reference_groups(self):
		result = get_placeholder_reference()
		self.assertIsInstance(result, list)
		groups = [block["grupo"] for block in result]
		self.assertIn("Escritório", groups)
		self.assertIn("Cliente", groups)
		self.assertIn("Obra", groups)
		self.assertIn("Subcontratos (obra)", groups)

	def test_build_context_company_and_customer(self):
		_ensure_engineering_settings()
		customer = create_test_customer(
			customer_name=_uid("Cliente Doc"),
			contacts=[{"contact_name": "Contato Teste", "phone": VALID_FIXO, "mobile": VALID_CELULAR, "email": "teste@example.com"}],
			addresses=[
				{
					"street": "Rua Teste",
					"number": "100",
					"district": "Centro",
					"city": "São Paulo",
					"state": "SP",
					"cep": "01001000",
					"is_primary": 1,
				}
			],
		)
		project = create_test_construction_project(
			customer=customer.name,
			address_street="Av Obra",
			address_number="50",
			city="Campinas",
			address_uf="SP",
			responsible_engineer="Eng. Teste",
			crea_number="999999/D-SP",
		)
		create_test_engineering_contract(
			project=project.name,
			base_value=25000,
			current_value=25000,
			adjustment_index="IPCA",
			installment_count=5,
		)

		context = _build_context(project.name)
		self.assertEqual(context["company_name"], "Escritório Teste Engenharia")
		self.assertEqual(context["company_cnpj"], "11222333000181")
		self.assertEqual(context["bank_pix"], "teste@example.com")
		self.assertEqual(context["customer_name"], customer.customer_name)
		self.assertEqual(context["nome"], customer.customer_name)
		self.assertEqual(context["project"], project.name)
		self.assertEqual(context["project_address_uf"], "SP")
		self.assertEqual(context["project_responsible_engineer"], "Eng. Teste")
		self.assertEqual(context["contract_value"], 25000)
		self.assertEqual(context["contract_adjustment_index"], "IPCA")
		self.assertEqual(context["contract_installment_count"], 5)
		self.assertIn("today", context)

	def test_placeholder_reference_matches_context(self):
		_ensure_engineering_settings()
		customer = create_test_customer(customer_name=_uid("Cliente Placeholder"))
		project = create_test_construction_project(customer=customer.name)
		create_test_engineering_contract(project=project.name, base_value=1000, current_value=1000)

		context = _build_context(project.name)
		missing = get_document_placeholder_keys() - set(context.keys())
		self.assertFalse(missing, f"Placeholders ausentes no contexto: {sorted(missing)}")

	def test_build_context_subcontracts(self):
		_ensure_engineering_settings()
		project = create_test_construction_project()
		supplier = create_test_supplier(supplier_name=_uid("João Pedreiro")).name
		create_test_subcontract(
			project=project.name,
			supplier=supplier,
			total_value=5000,
			payments=[
				{"payment_date": "2026-01-15", "amount": 2000, "payment_method": "PIX"},
				{"payment_date": "2026-02-10", "amount": 3000, "payment_method": "TED"},
			],
		)

		context = _build_context(project.name)
		self.assertEqual(context["subcontract_count"], 1)
		self.assertEqual(context["subcontract_total_value"], 5000)
		self.assertEqual(context["subcontract_total_paid"], 5000)
		self.assertEqual(context["subcontract_outstanding"], 0)
		self.assertEqual(len(context["subcontracts"]), 1)
		row = context["subcontracts"][0]
		self.assertEqual(row["total_value"], 5000)
		self.assertEqual(len(row["payments"]), 2)
		self.assertEqual(row["payments"][0]["amount"], 2000)
		self.assertEqual(row["payments"][0]["payment_method"], "PIX")

	def test_get_available_kits_with_templates(self):
		template_name = _create_test_document_template()
		if not template_name:
			self.skipTest("python-docx não instalado")

		kit_name = _uid("Kit Docs")
		frappe.get_doc(
			{
				"doctype": "Document Kit",
				"kit_name": kit_name,
				"templates": [{"document_template": template_name, "sort_order": 0}],
			}
		).insert(ignore_permissions=True)

		kits = get_available_kits()
		match = next((k for k in kits if k.get("kit_name") == kit_name), None)
		self.assertIsNotNone(match)
		self.assertIn(template_name, match["templates"])

	def test_generate_project_documents_batch(self):
		try:
			from docxtpl import DocxTemplate  # noqa: F401
		except ImportError:
			self.skipTest("docxtpl não instalado")

		project = create_test_construction_project()
		template_names = []
		for idx in range(2):
			name = _create_test_document_template(f"Doc {idx}: {{{{ customer_name }}}}")
			if not name:
				self.skipTest("python-docx não instalado")
			template_names.append(name)

		result = generate_project_documents(project.name, json.dumps(template_names))
		self.assertEqual(result["total"], 2)
		self.assertEqual(len(result["generated"]), 2)
		self.assertFalse(result["failures"])
