import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, flt, today

from engenharia.project_hub import get_project_counts, get_project_hub_data
from engenharia.tests.test_setup import (
	create_test_construction_project,
	create_test_deadline,
	create_test_project_stage,
	create_test_work_cost,
)
from engenharia.tests.test_subcontract import create_test_subcontract


class TestProjectHub(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_hub_returns_all_sections(self):
		project = create_test_construction_project()
		create_test_project_stage(project=project.name)

		data = get_project_hub_data(project.name)

		for key in (
			"stages",
			"deadlines",
			"permits",
			"tasks",
			"communications",
			"measurements",
			"timelogs",
			"documents",
		):
			self.assertIn(key, data)

	def test_hub_documents_reflects_records(self):
		from engenharia.engenharia.doctype.project_document.test_project_document import (
			_create_test_file_url,
		)
		from engenharia.tests.test_setup import ensure_test_document_category

		project = create_test_construction_project()
		ensure_test_document_category("Memorial")
		frappe.get_doc(
			{
				"doctype": "Project Document",
				"project": project.name,
				"category": "Memorial",
				"status": "Rascunho",
				"source": "Upload Manual",
				"file": _create_test_file_url(),
			}
		).insert(ignore_permissions=True)

		data = get_project_hub_data(project.name)
		self.assertEqual(len(data["documents"]), 1)
		self.assertEqual(data["documents"][0]["category"], "Memorial")

	def test_hub_stages_match_db(self):
		project = create_test_construction_project()
		create_test_project_stage(project=project.name)
		create_test_project_stage(project=project.name)

		data = get_project_hub_data(project.name)

		self.assertEqual(len(data["stages"]), 2)

	def test_financial_only_for_manager(self):
		project = create_test_construction_project()
		data = get_project_hub_data(project.name)
		self.assertIsInstance(data, dict)
		if "Engenharia Manager" in frappe.get_roles():
			self.assertIn("financial", data)
			self.assertIsInstance(data["financial"], dict)

	def test_financial_summary_uses_consolidated_costs(self):
		if "Engenharia Manager" not in frappe.get_roles():
			return

		project = create_test_construction_project()
		frappe.db.set_value("Construction Project", project.name, "spec_project_total", 50000)

		create_test_work_cost(project=project.name, amount=1000, status="Open", payments=[])
		create_test_subcontract(
			project=project.name,
			total_value=3000,
			payments=[{"payment_date": today(), "amount": 1000}],
		)

		summary = get_project_hub_data(project.name)["financial"]["summary"]

		self.assertEqual(flt(summary["budget_total"]), 50000)
		self.assertEqual(flt(summary["total_realized_committed"]), 4000)
		self.assertEqual(flt(summary["total_realized_paid"]), 1000)
		self.assertEqual(flt(summary["outstanding_payable"]), 3000)
		self.assertEqual(flt(summary["total_realized_outstanding"]), 3000)

	def test_hub_deadlines_urgency(self):
		project = create_test_construction_project()
		create_test_deadline(
			project=project.name,
			due_date=add_days(today(), -5),
			status="Pendente",
		)

		data = get_project_hub_data(project.name)
		overdue = [row for row in data["deadlines"] if row["urgency"] == "overdue"]
		self.assertGreater(len(overdue), 0)

	def test_get_project_counts_returns_all_keys(self):
		project = create_test_construction_project()
		counts = get_project_counts(project.name)

		expected_keys = [
			"stages",
			"contracts",
			"payments",
			"costs",
			"subcontracts",
			"reimbursables",
			"commissions",
			"deadlines",
			"permits",
			"tasks",
			"communications",
			"timelogs",
			"measurements",
			"items",
			"documents",
		]
		for key in expected_keys:
			self.assertIn(key, counts)

	def test_get_project_counts_reflects_data(self):
		project = create_test_construction_project()
		create_test_project_stage(project=project.name)
		create_test_project_stage(project=project.name)

		counts = get_project_counts(project.name)

		self.assertEqual(counts["stages"], 2)
