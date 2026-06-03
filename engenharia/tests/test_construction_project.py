import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import _uid, create_test_construction_project, create_test_customer
from engenharia.titles import TITLE_SEPARATOR, join_title_parts


from engenharia.engenharia.doctype.construction_project.construction_project import create_project_item
from engenharia.tests.test_project_item import create_test_technical_item_cylinder


class TestConstructionProject(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_crud(self):
		project = create_test_construction_project()
		self.assertTrue(frappe.db.exists("Construction Project", project.name))
		project.status = "Em andamento"
		project.save(ignore_permissions=True)
		name = project.name
		project.delete(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Construction Project", name))

	def test_compose_title_with_customer_and_city(self):
		customer = create_test_customer(customer_name=f"Construtora {_uid()}")
		project = create_test_construction_project(
			customer=customer.name,
			city="Campinas",
		)
		expected_descritor = f"{customer.customer_name} - Campinas"
		expected_title = join_title_parts(project.name, expected_descritor)
		self.assertEqual(project.title, expected_title)
		self.assertIn(TITLE_SEPARATOR, project.title)
		self.assertIn("Campinas", project.title)

	def test_create_project_item_from_project(self):
		item = create_test_technical_item_cylinder()
		project = create_test_construction_project()
		name = create_project_item(project=project.name, technical_item=item.name)
		doc = frappe.get_doc("Project Item", name)
		self.assertEqual(doc.project, project.name)
		self.assertEqual(doc.technical_item, item.name)
		self.assertEqual(len(doc.parameter_values), 3)

	def test_title_updates_when_city_changes(self):
		project = create_test_construction_project(city="Santos")
		customer_name = frappe.db.get_value("Customer", project.customer, "customer_name")
		project.city = "Guarujá"
		project.save(ignore_permissions=True)
		project.reload()
		expected = join_title_parts(project.name, f"{customer_name} - Guarujá")
		self.assertEqual(project.title, expected)
