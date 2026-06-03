import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.specifications import expand_specification_template, validate_field_key
from engenharia.tests.test_setup import _uid


def create_test_technical_item_with_fields(**kwargs):
	fields = kwargs.pop(
		"fields",
		[
			{
				"field_key": "value",
				"label": "Valor",
				"unit": kwargs.pop("default_unit", "m²"),
				"data_type": "Número",
				"required": 1,
				"sort_order": 1,
			}
		],
	)
	data = {
		"doctype": "Technical Item",
		"item_name": kwargs.pop("item_name", _uid("Item Tecnico")),
		"item_key": kwargs.pop("item_key", None),
		"data_type": "Número",
		"category": "Estrutural",
		"fields": fields,
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


class TestSpecifications(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_field_key_validation(self):
		self.assertEqual(validate_field_key("volume_m3"), "volume_m3")
		with self.assertRaises(frappe.ValidationError):
			validate_field_key("Volume")

	def test_technical_item_requires_fields(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Technical Item",
					"item_name": _uid("Sem campos"),
					"data_type": "Número",
					"category": "Geral",
				}
			).insert(ignore_permissions=True)

	def test_expand_specification_template(self):
		item = create_test_technical_item_with_fields()
		rows = expand_specification_template(
			frappe._dict(
				{
					"technical_item": item.name,
					"instance_label": "Instância A",
					"value": "1000",
				}
			)
		)
		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0]["value"], "1000")
		self.assertEqual(rows[0]["field_key"], "value")

	def test_seed_technical_items(self):
		from engenharia.setup.seed import ensure_technical_item_templates

		ensure_technical_item_templates()
		self.assertTrue(frappe.db.exists("Technical Item", "Fossa séptica"))
		fossa = frappe.get_doc("Technical Item", "Fossa séptica")
		self.assertEqual(fossa.item_key, "fossa_septica")
		self.assertEqual(len(fossa.fields), 6)
