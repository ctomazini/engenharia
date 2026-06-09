import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from engenharia.project_hub import get_project_counts, get_project_hub_data
from engenharia.tests.test_setup import (
	create_test_construction_project,
	create_test_deadline,
	create_test_project_stage,
)


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
		):
			self.assertIn(key, data)

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
		]
		for key in expected_keys:
			self.assertIn(key, counts)

	def test_get_project_counts_reflects_data(self):
		project = create_test_construction_project()
		create_test_project_stage(project=project.name)
		create_test_project_stage(project=project.name)

		counts = get_project_counts(project.name)

		self.assertEqual(counts["stages"], 2)
