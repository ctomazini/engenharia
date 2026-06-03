import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import _uid


class TestPermitType(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_crud(self):
		type_name = _uid("Alvará Teste")
		doc = frappe.get_doc({"doctype": "Permit Type", "type_name": type_name}).insert(
			ignore_permissions=True
		)
		self.assertEqual(doc.name, type_name)
		self.assertTrue(frappe.db.exists("Permit Type", type_name))

	def test_type_name_required(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc({"doctype": "Permit Type"}).insert(ignore_permissions=True)

	def test_permit_link_resolves(self):
		type_name = _uid("Habite-se Teste")
		frappe.get_doc({"doctype": "Permit Type", "type_name": type_name}).insert(
			ignore_permissions=True
		)
		from engenharia.tests.test_setup import create_test_construction_project

		project = create_test_construction_project()
		permit = frappe.get_doc(
			{
				"doctype": "Permit",
				"project": project.name,
				"permit_type": type_name,
			}
		).insert(ignore_permissions=True)
		self.assertEqual(permit.permit_type, type_name)
		self.assertEqual(frappe.db.get_value("Permit Type", permit.permit_type, "type_name"), type_name)
