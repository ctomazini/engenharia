import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import _uid


class TestStageType(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _create(self, **kwargs):
		data = {
			"doctype": "Stage Type",
			"stage_name": _uid("Etapa"),
			"default_order": 1,
			**kwargs,
		}
		doc = frappe.get_doc(data)
		doc.insert(ignore_permissions=True)
		return doc

	def test_crud(self):
		doc = self._create(default_order=10)
		self.assertEqual(doc.default_order, 10)
		doc.default_order = 20
		doc.save(ignore_permissions=True)
		name = doc.name
		doc.delete(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Stage Type", name))
