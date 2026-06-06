import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, get_first_day, get_last_day, today

from engenharia.dashboard.kpis import build_kpis
from engenharia.tests.test_setup import (
	_uid,
	create_test_construction_project,
	create_test_cost_category,
	create_test_supplier,
)
from engenharia.work_costs import FUNDED_BY_CLIENT, FUNDED_BY_OFFICE, get_subcontract_outstanding_total


def create_test_subcontract(project=None, supplier=None, **kwargs):
	if not project:
		project = create_test_construction_project().name
	if not supplier:
		supplier = create_test_supplier().name
	data = {
		"doctype": "Subcontract",
		"project": project,
		"supplier": supplier,
		"total_value": kwargs.pop("total_value", 5000),
		**kwargs,
	}
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


class TestSubcontract(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_default_funded_by_office(self):
		doc = create_test_subcontract(total_value=5000)
		self.assertEqual(doc.funded_by, FUNDED_BY_OFFICE)

	def test_client_funded_excluded_from_cash_flow_kpis(self):
		project = create_test_construction_project().name
		hoje = today()
		month_start = get_first_day(hoje)
		month_end = get_last_day(hoje)
		period_end = frappe.utils.add_days(hoje, 7)
		before = build_kpis(hoje, period_end, month_start, month_end)

		create_test_subcontract(
			project=project,
			total_value=5000,
			funded_by=FUNDED_BY_CLIENT,
			payments=[{"payment_date": hoje, "amount": 2000}],
		)
		after_client = build_kpis(hoje, period_end, month_start, month_end)
		self.assertEqual(after_client["month_costs"]["amount"], before["month_costs"]["amount"])

		outstanding_before = get_subcontract_outstanding_total()
		create_test_subcontract(
			project=project,
			total_value=3000,
			funded_by=FUNDED_BY_OFFICE,
		)
		self.assertEqual(get_subcontract_outstanding_total(), outstanding_before + 3000)

	def test_create_subcontract(self):
		doc = create_test_subcontract(total_value=5000)
		self.assertEqual(doc.status, "Open")
		self.assertEqual(flt(doc.total_paid), 0)
		self.assertEqual(flt(doc.outstanding), 5000)

	def test_partial_payment(self):
		doc = create_test_subcontract(
			total_value=5000,
			payments=[{"payment_date": "2026-01-15", "amount": 2000, "reference": "PIX-001"}],
		)
		self.assertEqual(doc.status, "Partially Paid")
		self.assertEqual(flt(doc.total_paid), 2000)
		self.assertEqual(flt(doc.outstanding), 3000)

	def test_full_payment(self):
		doc = create_test_subcontract(
			total_value=5000,
			payments=[
				{"payment_date": "2026-01-15", "amount": 2000},
				{"payment_date": "2026-02-10", "amount": 3000},
			],
		)
		self.assertEqual(doc.status, "Paid")
		self.assertEqual(flt(doc.outstanding), 0)

	def test_overpayment_throws(self):
		with self.assertRaises(ValidationError):
			create_test_subcontract(
				total_value=1000,
				payments=[{"payment_date": "2026-01-15", "amount": 1500}],
			)

	def test_title_composition(self):
		supplier = create_test_supplier(supplier_name=_uid("João Pedreiro")).name
		doc = create_test_subcontract(supplier=supplier, total_value=5000)
		supplier_name = frappe.db.get_value("Supplier", supplier, "supplier_name")
		self.assertIn(doc.name, doc.title)
		self.assertIn(supplier_name, doc.title)

	def test_amendment_total_value(self):
		doc = create_test_subcontract(
			total_value=5000,
			payments=[{"payment_date": "2026-01-15", "amount": 2000}],
		)
		doc.total_value = 6000
		doc.amendment_remarks = "Serviço ampliado"
		doc.save(ignore_permissions=True)
		self.assertEqual(flt(doc.outstanding), 4000)
		self.assertEqual(doc.status, "Partially Paid")

	def test_cancelled_immutable(self):
		doc = create_test_subcontract(total_value=3000)
		doc.status = "Cancelled"
		doc.save(ignore_permissions=True)
		doc.description = "tentativa de alteração"
		with self.assertRaises(ValidationError):
			doc.save(ignore_permissions=True)

	def test_combined_project_cost(self):
		from engenharia.work_costs import get_combined_project_cost

		project = create_test_construction_project().name
		category = create_test_cost_category().name
		frappe.get_doc(
			{
				"doctype": "Work Cost",
				"project": project,
				"cost_category": category,
				"amount": 1000,
				"date": "2026-01-10",
				"status": "Pago",
				"description": "Material avulso",
			}
		).insert(ignore_permissions=True)
		create_test_subcontract(
			project=project,
			total_value=5000,
			payments=[
				{"payment_date": "2026-01-15", "amount": 2000},
				{"payment_date": "2026-02-10", "amount": 3000},
			],
		)
		self.assertEqual(get_combined_project_cost(project), 6000)
