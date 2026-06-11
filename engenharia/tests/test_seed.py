import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.setup.seed import (
	DEFAULT_BUILDING_TYPES,
	DEFAULT_DOCUMENT_CATEGORIES,
	DEFAULT_PERMIT_TYPES,
	ensure_default_building_types,
	ensure_default_cost_categories,
	ensure_default_document_categories,
	ensure_default_permit_types,
	ensure_default_stage_types,
	ensure_engineering_settings,
)


class TestSeed(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_seed_idempotent(self):
		ensure_default_cost_categories()
		count_before = frappe.db.count("Cost Category")
		ensure_default_cost_categories()
		self.assertEqual(frappe.db.count("Cost Category"), count_before)

		ensure_default_stage_types()
		count_stages = frappe.db.count("Stage Type")
		ensure_default_stage_types()
		self.assertEqual(frappe.db.count("Stage Type"), count_stages)

		ensure_engineering_settings()
		self.assertTrue(frappe.db.exists("Engineering Settings", "Engineering Settings"))

	def test_seed_document_categories_idempotent(self):
		ensure_default_document_categories()
		count_before = frappe.db.count("Document Category")
		ensure_default_document_categories()
		self.assertEqual(frappe.db.count("Document Category"), count_before)
		for category_name in DEFAULT_DOCUMENT_CATEGORIES:
			self.assertTrue(frappe.db.exists("Document Category", category_name))

	def test_seed_building_types_idempotent(self):
		ensure_default_building_types()
		count_before = frappe.db.count("Building Type")
		ensure_default_building_types()
		self.assertEqual(frappe.db.count("Building Type"), count_before)
		for type_name in DEFAULT_BUILDING_TYPES:
			self.assertTrue(frappe.db.exists("Building Type", type_name))

	def test_seed_permit_types_idempotent(self):
		ensure_default_permit_types()
		count_before = frappe.db.count("Permit Type")
		ensure_default_permit_types()
		self.assertEqual(frappe.db.count("Permit Type"), count_before)
		for type_name in DEFAULT_PERMIT_TYPES:
			self.assertTrue(frappe.db.exists("Permit Type", type_name))
