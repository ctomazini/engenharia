import os

import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase

from engenharia.project_document_naming import compose_project_document_filename
from engenharia.tests.test_setup import (
	_uid,
	create_test_construction_project,
	create_test_permit,
	ensure_test_document_category,
)


def _create_test_file_url():
	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": f"proj_doc_{frappe.generate_hash(length=6)}.txt",
			"content": b"test project document",
			"is_private": 1,
		}
	)
	file_doc.save(ignore_permissions=True)
	return file_doc.file_url


class TestProjectDocument(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_create_project_document(self):
		project = create_test_construction_project()
		ensure_test_document_category("Memorial")
		doc = frappe.get_doc(
			{
				"doctype": "Project Document",
				"project": project.name,
				"category": "Memorial",
				"status": "Rascunho",
				"source": "Upload Manual",
				"file": _create_test_file_url(),
			}
		).insert(ignore_permissions=True)

		self.assertTrue(doc.name.startswith("DOC-"))
		self.assertEqual(doc.category, "Memorial")
		self.assertEqual(doc.title, f"{project.name} — Memorial")
		self.assertEqual(doc.customer, project.customer)

	def test_auto_compose_title_with_version_and_descriptor(self):
		project = create_test_construction_project()
		ensure_test_document_category("ART")
		doc = frappe.get_doc(
			{
				"doctype": "Project Document",
				"project": project.name,
				"category": "ART",
				"status": "Rascunho",
				"file": _create_test_file_url(),
				"version": "Rev_01",
				"title_descriptor": "Estrutural",
			}
		).insert(ignore_permissions=True)

		self.assertEqual(
			doc.title,
			f"{project.name} — ART — Rev_01 — Estrutural",
		)

	def test_file_rename_uses_underscore_parts(self):
		project = create_test_construction_project()
		ensure_test_document_category("Memorial")
		file_url = _create_test_file_url()
		version = f"Rev_{frappe.generate_hash(length=6)}"
		doc = frappe.get_doc(
			{
				"doctype": "Project Document",
				"project": project.name,
				"category": "Memorial",
				"status": "Rascunho",
				"file": file_url,
				"version": version,
			}
		).insert(ignore_permissions=True)

		expected = compose_project_document_filename(
			project.name,
			"Memorial",
			version,
			None,
			file_url,
		)
		file_doc = frappe.get_doc("File", {"file_url": doc.file})
		file_name = file_doc.file_name
		disk_path = file_doc.get_full_path()
		self.assertEqual(file_name, expected)
		self.assertEqual(doc.file.split("/")[-1], expected)
		self.assertTrue(os.path.exists(disk_path))
		self.assertEqual(os.path.basename(disk_path), expected)
		self.assertIn("_", file_name)
		self.assertTrue(file_name.startswith(project.name))

	def test_permit_must_match_project(self):
		project_a = create_test_construction_project()
		project_b = create_test_construction_project()
		permit = create_test_permit(project=project_b.name)
		ensure_test_document_category("Protocolo")

		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Project Document",
					"project": project_a.name,
					"category": "Protocolo",
					"status": "Protocolado",
					"file": _create_test_file_url(),
					"related_permit": permit.name,
				}
			).insert(ignore_permissions=True)

	def test_status_options(self):
		meta = frappe.get_meta("Project Document")
		status_field = meta.get_field("status")
		options = [option.strip() for option in (status_field.options or "").split("\n")]
		for expected in ("Rascunho", "Assinado", "Protocolado", "Aprovado", "Vencido", "Substituído"):
			self.assertIn(expected, options)
