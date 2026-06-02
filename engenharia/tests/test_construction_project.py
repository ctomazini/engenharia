import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import _uid, create_test_construction_project, create_test_customer
from engenharia.titles import TITLE_SEPARATOR, join_title_parts


def create_test_technical_item(**kwargs):
	data = {
		"doctype": "Technical Item",
		"item_name": _uid("Item Tecnico"),
		"default_unit": "m²",
		"data_type": "Número",
		"category": "Estrutural",
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


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

	def test_specifications_child_table(self):
		item = create_test_technical_item(default_unit="m")
		project = create_test_construction_project(
			specifications=[
				{
					"technical_item": item.name,
					"value": "120",
					"remarks": "Teste",
				}
			]
		)
		self.assertEqual(len(project.specifications), 1)
		self.assertEqual(project.specifications[0].technical_item, item.name)
		self.assertEqual(project.specifications[0].unit, "m")

	def test_title_updates_when_city_changes(self):
		project = create_test_construction_project(city="Santos")
		customer_name = frappe.db.get_value("Customer", project.customer, "customer_name")
		project.city = "Guarujá"
		project.save(ignore_permissions=True)
		project.reload()
		expected = join_title_parts(project.name, f"{customer_name} - Guarujá")
		self.assertEqual(project.title, expected)
