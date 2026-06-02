import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import _gerar_cnpj_valido, _uid


class TestSupplier(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _create(self, **kwargs):
		data = {
			"doctype": "Supplier",
			"supplier_name": _uid("Supplier"),
			**kwargs,
		}
		doc = frappe.get_doc(data)
		doc.insert(ignore_permissions=True)
		return doc

	def test_crud(self):
		doc = self._create(cnpj=_gerar_cnpj_valido(), category="Material")
		self.assertTrue(frappe.db.exists("Supplier", doc.name))
		doc.category = "Serviço"
		doc.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Supplier", doc.name, "category"), "Serviço")
		name = doc.name
		doc.delete(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Supplier", name))

	def test_duplicate_name_rejected(self):
		name = _uid("Supplier Unico")
		self._create(supplier_name=name)
		with self.assertRaises(frappe.DuplicateEntryError):
			self._create(supplier_name=name)
