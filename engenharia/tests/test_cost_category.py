import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import _uid


class TestCostCategory(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _create(self, **kwargs):
		data = {
			"doctype": "Cost Category",
			"category_name": _uid("Categoria"),
			**kwargs,
		}
		doc = frappe.get_doc(data)
		doc.insert(ignore_permissions=True)
		return doc

	def test_crud(self):
		doc = self._create()
		self.assertTrue(frappe.db.exists("Cost Category", doc.name))
		doc.category_name = f"Updated {_uid()}"
		doc.save(ignore_permissions=True)
		name = doc.name
		doc.delete(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Cost Category", name))
