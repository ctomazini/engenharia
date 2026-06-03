import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import _uid


class TestTechnicalItem(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _create(self, **kwargs):
		fields = kwargs.pop(
			"fields",
			[
				{
					"field_key": "value",
					"label": "Valor",
					"unit": "m²",
					"data_type": "Número",
					"required": 1,
					"sort_order": 1,
				}
			],
		)
		data = {
			"doctype": "Technical Item",
			"item_name": _uid("Item"),
			"default_unit": "m²",
			"data_type": "Número",
			"category": "Estrutural",
			"fields": fields,
			**kwargs,
		}
		doc = frappe.get_doc(data)
		doc.insert(ignore_permissions=True)
		return doc

	def test_crud(self):
		doc = self._create()
		self.assertEqual(doc.default_unit, "m²")
		doc.data_type = "Texto"
		doc.save(ignore_permissions=True)
		name = doc.name
		doc.delete(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Technical Item", name))
