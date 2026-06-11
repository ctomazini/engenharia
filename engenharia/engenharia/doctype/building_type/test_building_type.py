import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import _uid, create_test_construction_project


class TestBuildingType(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_crud(self):
		type_name = _uid("Residencial Teste")
		doc = frappe.get_doc(
			{"doctype": "Building Type", "building_type_name": type_name}
		).insert(ignore_permissions=True)
		self.assertEqual(doc.name, type_name)
		self.assertTrue(frappe.db.exists("Building Type", type_name))

	def test_type_name_required(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc({"doctype": "Building Type"}).insert(ignore_permissions=True)

	def test_project_link_resolves(self):
		type_name = _uid("Comercial Teste")
		frappe.get_doc(
			{"doctype": "Building Type", "building_type_name": type_name}
		).insert(ignore_permissions=True)
		project = create_test_construction_project(building_type=type_name)
		self.assertEqual(project.building_type, type_name)
