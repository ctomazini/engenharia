import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, get_first_day, get_last_day, today

from engenharia.dashboard.kpis import build_kpis
from engenharia.tests.test_setup import (
	create_test_construction_project,
	create_test_cost_category,
	create_test_project_stage,
	create_test_supplier,
	create_test_work_cost,
)
from engenharia.work_costs import (
	FUNDED_BY_CLIENT,
	FUNDED_BY_OFFICE,
	get_work_cost_totals_by_category,
	get_work_cost_totals_by_stage,
	get_work_cost_totals_by_supplier,
)


class TestWorkCost(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_default_funded_by_office(self):
		cost = create_test_work_cost(amount=100)
		self.assertEqual(cost.funded_by, FUNDED_BY_OFFICE)

	def test_client_funded_excluded_from_month_kpis(self):
		project = create_test_construction_project().name
		hoje = today()
		month_start = get_first_day(hoje)
		month_end = get_last_day(hoje)
		period_end = frappe.utils.add_days(hoje, 7)
		before = build_kpis(hoje, period_end, month_start, month_end)

		create_test_work_cost(project=project, amount=3000, funded_by=FUNDED_BY_CLIENT)
		after_client = build_kpis(hoje, period_end, month_start, month_end)
		self.assertEqual(after_client["month_costs"]["amount"], before["month_costs"]["amount"])

		create_test_work_cost(project=project, amount=1000, funded_by=FUNDED_BY_OFFICE)
		after_office = build_kpis(hoje, period_end, month_start, month_end)
		self.assertEqual(after_office["month_costs"]["amount"], before["month_costs"]["amount"] + 1000)

	def test_crud(self):
		cost = create_test_work_cost(amount=2500)
		self.assertTrue(frappe.db.exists("Work Cost", cost.name))
		self.assertTrue(cost.title.startswith(cost.name))
		name = cost.name
		cost.delete(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Work Cost", name))

	def test_customer_from_project(self):
		project = create_test_construction_project()
		cost = create_test_work_cost(project=project.name, amount=100)
		self.assertEqual(cost.customer, project.customer)

	def test_partial_payments(self):
		cost = create_test_work_cost(
			amount=3000,
			status="Open",
			payments=[],
		)
		self.assertEqual(cost.status, "Open")
		self.assertEqual(flt(cost.outstanding), 3000)

		cost.append("payments", {"payment_date": today(), "amount": 1500})
		cost.save(ignore_permissions=True)
		cost.reload()
		self.assertEqual(cost.status, "Partially Paid")
		self.assertEqual(flt(cost.total_paid), 1500)
		self.assertEqual(flt(cost.outstanding), 1500)

		cost.append("payments", {"payment_date": today(), "amount": 1500})
		cost.save(ignore_permissions=True)
		cost.reload()
		self.assertEqual(cost.status, "Paid")
		self.assertEqual(flt(cost.outstanding), 0)

	def test_cancelled_immutable(self):
		cost = create_test_work_cost(status="Cancelado")
		cost.amount = 999
		with self.assertRaises(ValidationError):
			cost.save(ignore_permissions=True)

	def test_aggregate_by_category(self):
		project = create_test_construction_project().name
		cat_a = create_test_cost_category().name
		cat_b = create_test_cost_category().name
		create_test_work_cost(project=project, amount=1000, cost_category=cat_a, status="Pago")
		create_test_work_cost(project=project, amount=500, cost_category=cat_b, status="Pago")
		create_test_work_cost(project=project, amount=300, status="Pendente")

		totals = get_work_cost_totals_by_category(project=project)
		self.assertEqual(totals[cat_a], 1000)
		self.assertEqual(totals[cat_b], 500)
		self.assertEqual(len(totals), 2)

	def test_aggregate_by_supplier(self):
		project = create_test_construction_project().name
		supplier = create_test_supplier().name
		create_test_work_cost(project=project, amount=800, supplier=supplier, status="Pago")
		totals = get_work_cost_totals_by_supplier(project=project)
		self.assertEqual(totals[supplier], 800)

	def test_aggregate_by_stage(self):
		project = create_test_construction_project().name
		stage = create_test_project_stage(project=project).name
		create_test_work_cost(project=project, amount=1200, stage=stage, status="Pago")
		totals = get_work_cost_totals_by_stage(project=project)
		self.assertEqual(totals[stage], 1200)

	def test_open_count_linked_project(self):
		from frappe.desk.notifications import get_open_count

		project = create_test_construction_project()
		cost = create_test_work_cost(project=project.name, amount=500)
		result = get_open_count("Work Cost", cost.name, '["Construction Project"]')
		internal = result["count"]["internal_links_found"]
		self.assertEqual(len(internal), 1)
		self.assertEqual(internal[0]["doctype"], "Construction Project")
		self.assertEqual(internal[0]["names"], [project.name])
