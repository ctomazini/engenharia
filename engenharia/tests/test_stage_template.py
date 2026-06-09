import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt

from engenharia.stage_template import apply_template_to_project, redistribute_stage_weights
from engenharia.tests.test_setup import create_test_construction_project, create_test_project_stage


class TestProjectStageTemplate(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_template_valid_weights(self):
		tpl = _create_template("Test Valid", [("Fundação", 60), ("Estrutura", 40)])
		self.assertEqual(tpl.doctype, "Project Stage Template")

	def test_template_invalid_weight_sum(self):
		self.assertRaises(
			frappe.ValidationError,
			_create_template,
			"Test Invalid",
			[("Fundação", 50), ("Estrutura", 30)],
		)

	def test_template_duplicate_stage_type(self):
		self.assertRaises(
			frappe.ValidationError,
			_create_template,
			"Test Dup",
			[("Fundação", 50), ("Fundação", 50)],
		)

	def test_apply_template_creates_stages(self):
		tpl = _create_template("Test Apply", [("Fundação", 70), ("Estrutura", 30)])
		project = create_test_construction_project(project_type=tpl.project_type)

		result = apply_template_to_project(project.name, tpl.project_type)

		self.assertEqual(result["created"], 2)
		stages = frappe.get_all(
			"Project Stage",
			filters={"project": project.name},
			fields=["stage_type", "weight", "progress"],
			order_by="order asc",
		)
		self.assertEqual(len(stages), 2)
		self.assertEqual(stages[0].stage_type, "Fundação")
		self.assertAlmostEqual(stages[0].weight, 70, places=1)
		self.assertEqual(stages[0].progress, 0)

	def test_apply_template_replaces_existing(self):
		tpl = _create_template("Test Replace", [("Fundação", 100)])
		project = create_test_construction_project(project_type=tpl.project_type)
		create_test_project_stage(project=project.name, progress=50)

		result = apply_template_to_project(project.name, tpl.project_type)

		stages = frappe.get_all("Project Stage", filters={"project": project.name})
		self.assertEqual(len(stages), 1)
		self.assertEqual(result["created"], 1)

	def test_redistribute_weights(self):
		project = create_test_construction_project()
		for _ in range(3):
			create_test_project_stage(project=project.name, weight=10)

		result = redistribute_stage_weights(project.name)

		self.assertEqual(result["count"], 3)
		stages = frappe.get_all(
			"Project Stage",
			filters={"project": project.name},
			fields=["weight"],
		)
		total = sum(flt(s.weight) for s in stages)
		self.assertAlmostEqual(total, 100, places=1)

	def test_stage_after_insert_syncs_progress(self):
		project = create_test_construction_project()
		create_test_project_stage(
			project=project.name, progress=80, weight=1, status="Em andamento"
		)

		project.reload()
		self.assertGreater(project.physical_progress, 0)

	def test_stage_on_trash_syncs_progress(self):
		project = create_test_construction_project()
		create_test_project_stage(project=project.name, progress=100, weight=1)
		s2 = create_test_project_stage(project=project.name, progress=0, weight=1)

		project.reload()
		progress_before = project.physical_progress

		frappe.delete_doc("Project Stage", s2.name)
		project.reload()
		self.assertGreaterEqual(project.physical_progress, progress_before)


def _create_template(name, stages, project_type="Execução"):
	unique_name = f"{name}-{frappe.generate_hash(length=6)}"

	for stage_name, _weight in stages:
		if not frappe.db.exists("Stage Type", stage_name):
			frappe.get_doc(
				{
					"doctype": "Stage Type",
					"stage_name": stage_name,
				}
			).insert(ignore_permissions=True)

	return frappe.get_doc(
		{
			"doctype": "Project Stage Template",
			"template_name": unique_name,
			"project_type": project_type,
			"stages": [
				{"stage_type": stage_name, "weight": weight, "sort_order": idx + 1}
				for idx, (stage_name, weight) in enumerate(stages)
			],
		}
	).insert(ignore_permissions=True)
