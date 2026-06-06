import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt

from engenharia.engenharia.doctype.commission.commission import sync_project_commission_outstanding
from engenharia.tests.test_setup import _uid, create_test_construction_project


def create_test_commission(project=None, **kwargs):
	if not project:
		project = create_test_construction_project().name
	data = {
		"doctype": "Commission",
		"construction_project": project,
		"commission_type": "Pré-Moldado",
		"supplier_name": kwargs.pop("supplier_name", _uid("PréMold")),
		"total_value": kwargs.pop("total_value", 10000),
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


class TestCommission(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_create_commission(self):
		doc = create_test_commission(total_value=10000)
		self.assertEqual(doc.status, "Open")
		self.assertEqual(flt(doc.total_paid), 0)
		self.assertEqual(flt(doc.outstanding), 10000)

	def test_partial_payment(self):
		doc = create_test_commission(
			total_value=10000,
			payments=[{"payment_date": "2026-01-15", "amount": 3000, "reference": "PIX-001"}],
		)
		self.assertEqual(doc.status, "Partially Paid")
		self.assertEqual(flt(doc.total_paid), 3000)
		self.assertEqual(flt(doc.outstanding), 7000)

	def test_full_payment(self):
		doc = create_test_commission(
			total_value=5000,
			payments=[
				{"payment_date": "2026-01-15", "amount": 2500},
				{"payment_date": "2026-02-15", "amount": 2500},
			],
		)
		self.assertEqual(doc.status, "Paid")
		self.assertEqual(flt(doc.outstanding), 0)

	def test_overpayment_throws(self):
		project = create_test_construction_project().name
		with self.assertRaises(ValidationError):
			create_test_commission(
				project=project,
				total_value=1000,
				payments=[{"payment_date": "2026-01-15", "amount": 1500}],
			)

	def test_title_composition(self):
		project = create_test_construction_project()
		project_title = frappe.db.get_value("Construction Project", project.name, "title")
		doc = create_test_commission(project=project.name, supplier_name="PréMold Ltda", total_value=8000)
		self.assertIn("PréMold Ltda", doc.title)
		self.assertIn(project_title, doc.title)

	def test_sync_project_commission_outstanding(self):
		if not frappe.get_meta("Construction Project").has_field("commission_outstanding"):
			self.skipTest("commission_outstanding não configurado no Construction Project")

		project = create_test_construction_project()
		create_test_commission(project=project.name, total_value=10000)
		create_test_commission(
			project=project.name,
			total_value=5000,
			payments=[{"payment_date": "2026-01-15", "amount": 2000}],
		)

		sync_project_commission_outstanding(project.name)
		total = flt(frappe.db.get_value("Construction Project", project.name, "commission_outstanding"))
		self.assertEqual(total, 13000)
