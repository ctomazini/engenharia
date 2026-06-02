import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import _uid


class TestPublicAgency(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _create(self, **kwargs):
		data = {
			"doctype": "Public Agency",
			"agency_name": _uid("Orgao"),
			"sphere": "Municipal",
			"city": "São Paulo",
			**kwargs,
		}
		doc = frappe.get_doc(data)
		doc.insert(ignore_permissions=True)
		return doc

	def test_crud(self):
		doc = self._create()
		self.assertEqual(doc.sphere, "Municipal")
		doc.city = "Campinas"
		doc.save(ignore_permissions=True)
		name = doc.name
		doc.delete(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Public Agency", name))
