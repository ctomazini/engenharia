import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.engenharia.api.costs import (
	SOURCE_REIMBURSABLE,
	SOURCE_SUBCONTRACT,
	SOURCE_WORK_COST,
	build_consolidated_costs,
	get_consolidated_costs,
)
from engenharia.engenharia.report.consolidated_cost.consolidated_cost import execute
from engenharia.tests.test_setup import (
	create_test_construction_project,
	create_test_cost_category,
	create_test_reimbursable_expense,
	create_test_work_cost,
)
from engenharia.tests.test_subcontract import create_test_subcontract


class TestConsolidatedCost(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_consolidated_costs_api(self):
		project = create_test_construction_project()
		category = create_test_cost_category().name
		wc = create_test_work_cost(
			project=project.name,
			amount=1000,
			cost_category=category,
			status="Pago",
		)
		re = create_test_reimbursable_expense(
			project=project.name,
			amount=500,
			expense_category=category,
			status="Reembolsado",
		)
		sub = create_test_subcontract(
			project=project.name,
			total_value=3000,
			payments=[{"payment_date": "2026-01-15", "amount": 1000}],
		)

		result = get_consolidated_costs(project.name)
		items = result["items"]
		self.assertEqual(len(items), 3)

		by_source = {row["source"]: row for row in items}
		self.assertIn(SOURCE_WORK_COST, by_source)
		self.assertIn(SOURCE_REIMBURSABLE, by_source)
		self.assertIn(SOURCE_SUBCONTRACT, by_source)

		wc_row = by_source[SOURCE_WORK_COST]
		self.assertEqual(wc_row["name"], wc.name)
		self.assertEqual(wc_row["source_label"], "Custo Direto")
		self.assertEqual(wc_row["source_doctype"], "Work Cost")
		self.assertEqual(wc_row["amount"], 1000)
		self.assertEqual(wc_row["paid"], 1000)
		self.assertEqual(wc_row["outstanding"], 0)
		self.assertIn("category", wc_row)
		self.assertIn("description", wc_row)
		self.assertIn("status", wc_row)

		re_row = by_source[SOURCE_REIMBURSABLE]
		self.assertEqual(re_row["name"], re.name)
		self.assertEqual(re_row["source_label"], "Despesa Reembolsável")
		self.assertEqual(re_row["paid"], 500)

		sub_row = by_source[SOURCE_SUBCONTRACT]
		self.assertEqual(sub_row["name"], sub.name)
		self.assertEqual(sub_row["source_label"], "Subcontrato")
		self.assertEqual(sub_row["amount"], 3000)
		self.assertEqual(sub_row["paid"], 1000)
		self.assertEqual(sub_row["outstanding"], 2000)

	def test_consolidated_costs_totals(self):
		project = create_test_construction_project()
		create_test_work_cost(project=project.name, amount=800, status="Pago")
		create_test_work_cost(project=project.name, amount=200, status="Pendente")
		create_test_reimbursable_expense(project=project.name, amount=300, status="A reembolsar")
		create_test_subcontract(
			project=project.name,
			total_value=1500,
			payments=[{"payment_date": "2026-01-15", "amount": 500}],
		)

		summary = build_consolidated_costs(project.name)["summary"]
		self.assertEqual(summary["total_amount"], 2800)
		self.assertEqual(summary["total_paid"], 1300)
		self.assertEqual(summary["total_outstanding"], 1500)
		self.assertIn("Custo Direto", summary["by_source"])
		self.assertIn("Despesa Reembolsável", summary["by_source"])
		self.assertIn("Subcontrato", summary["by_source"])

	def test_consolidated_costs_filters_cancelled(self):
		project = create_test_construction_project()
		create_test_work_cost(project=project.name, amount=900, status="Pago")
		create_test_work_cost(project=project.name, amount=999, status="Cancelado")
		create_test_reimbursable_expense(project=project.name, amount=400, status="Reembolsado")
		create_test_reimbursable_expense(project=project.name, amount=888, status="Cancelado")
		create_test_subcontract(project=project.name, total_value=2000)
		cancelled_sub = create_test_subcontract(project=project.name, total_value=777)
		frappe.db.set_value("Subcontract", cancelled_sub.name, "status", "Cancelled")

		items = build_consolidated_costs(project.name)["items"]
		names = {row["name"] for row in items}
		self.assertEqual(len(items), 3)
		self.assertNotIn(cancelled_sub.name, names)

	def test_consolidated_costs_permission(self):
		user = "test_consolidated_cost@example.com"
		if not frappe.db.exists("User", user):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user,
					"first_name": "Test",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)

		project = create_test_construction_project()
		frappe.set_user(user)
		try:
			with self.assertRaises(frappe.PermissionError):
				get_consolidated_costs(project.name)
		finally:
			frappe.set_user("Administrator")

	def test_report_returns_data(self):
		project = create_test_construction_project()
		create_test_work_cost(project=project.name, amount=1200, status="Pago")
		create_test_reimbursable_expense(project=project.name, amount=350, status="Reembolsado")
		create_test_subcontract(project=project.name, total_value=2500, total_paid=800)

		columns, data, _msg, chart, summary = execute({"project": project.name})
		self.assertTrue(columns)
		self.assertEqual(len(data), 3)
		self.assertIsNotNone(chart)
		self.assertTrue(summary)
		self.assertTrue(any(row.get("source_doc") for row in data))
