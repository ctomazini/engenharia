import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import _uid


class TestTechnicalItem(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _create(self, **kwargs):
		data = {
			"doctype": "Technical Item",
			"item_name": _uid("Item"),
			"default_unit": "m²",
			"data_type": "Número",
			"category": "Estrutural",
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
