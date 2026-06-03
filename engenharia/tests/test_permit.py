import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import create_test_construction_project, create_test_permit


class TestPermit(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_valid_crud(self):
		permit = create_test_permit()
		self.assertTrue(permit.name)
		self.assertTrue(permit.name.startswith("PROT-"))

	def test_customer_via_project(self):
		project = create_test_construction_project()
		permit = create_test_permit(project=project.name)
		self.assertEqual(permit.customer, project.customer)

	def test_composed_title(self):
		project = create_test_construction_project()
		customer_name = frappe.db.get_value("Customer", project.customer, "customer_name")
		permit = create_test_permit(project=project.name)
		self.assertIn(permit.name, permit.title)
		self.assertIn(customer_name, permit.title)

	def test_without_project_fails(self):
		with self.assertRaises((MandatoryError, ValidationError)):
			frappe.get_doc(
				{
					"doctype": "Permit",
					"permit_type": "Alvará",
				}
			).insert(ignore_permissions=True)

	def test_permit_types(self):
		for permit_type in ("Alvará", "Habite-se", "Licença Ambiental", "ART/RRT"):
			permit = create_test_permit(permit_type=permit_type)
			self.assertEqual(permit.permit_type, permit_type)
			self.assertTrue(frappe.db.exists("Permit Type", permit_type))
