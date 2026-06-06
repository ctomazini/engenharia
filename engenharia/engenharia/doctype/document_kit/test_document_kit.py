import os
import tempfile

import frappe
from frappe.exceptions import DuplicateEntryError, ValidationError
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import _uid


def _create_test_document_template():
	try:
		from docx import Document as DocxDocument
	except ImportError:
		return None

	with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
		doc = DocxDocument()
		doc.add_paragraph("Kit test {{ customer_name }}")
		doc.save(tmp.name)
		tmp_path = tmp.name

	try:
		file_doc = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": f"template_kit_{frappe.generate_hash(length=6)}.docx",
				"is_private": 1,
			}
		)
		with open(tmp_path, "rb") as handle:
			file_doc.content = handle.read()
		file_doc.save(ignore_permissions=True)

		template = frappe.get_doc(
			{
				"doctype": "Document Template",
				"template_name": _uid("Template Kit"),
				"document_type": "Contrato",
				"document_file": file_doc.file_url,
				"enabled": 1,
			}
		).insert(ignore_permissions=True)
		return template.name
	finally:
		if os.path.exists(tmp_path):
			os.unlink(tmp_path)


class TestDocumentKit(FrappeTestCase):
	def setUp(self):
		self.template_name = _create_test_document_template()
		if not self.template_name:
			self.skipTest("python-docx não instalado")

	def tearDown(self):
		frappe.db.rollback()

	def test_create_kit_with_template(self):
		kit_name = _uid("Kit Teste")
		kit = frappe.get_doc(
			{
				"doctype": "Document Kit",
				"kit_name": kit_name,
				"templates": [{"document_template": self.template_name, "sort_order": 0}],
			}
		).insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Document Kit", kit.name))
		self.assertEqual(len(kit.templates), 1)

	def test_kit_name_required(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Document Kit",
					"templates": [{"document_template": self.template_name, "sort_order": 0}],
				}
			).insert(ignore_permissions=True)

	def test_templates_required(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Document Kit",
					"kit_name": _uid("Kit Sem Template"),
				}
			).insert(ignore_permissions=True)

	def test_duplicate_kit_name(self):
		kit_name = _uid("Kit Dup")
		frappe.get_doc(
			{
				"doctype": "Document Kit",
				"kit_name": kit_name,
				"templates": [{"document_template": self.template_name, "sort_order": 0}],
			}
		).insert(ignore_permissions=True)
		with self.assertRaises((DuplicateEntryError, frappe.UniqueValidationError)):
			frappe.get_doc(
				{
					"doctype": "Document Kit",
					"kit_name": kit_name,
					"templates": [{"document_template": self.template_name, "sort_order": 0}],
				}
			).insert(ignore_permissions=True)
