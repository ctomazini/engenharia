import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.project_progress import calculate_physical_progress, sync_project_physical_progress
from engenharia.tests.test_setup import create_test_construction_project, create_test_project_stage


class TestProjectProgress(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_weighted_physical_progress(self):
		project = create_test_construction_project()
		create_test_project_stage(project=project.name, progress=100, weight=2, status="Concluída")
		create_test_project_stage(project=project.name, progress=0, weight=1, status="Não iniciada")

		progress = calculate_physical_progress(project.name)
		self.assertAlmostEqual(progress, 66.7, places=1)

	def test_stage_update_syncs_project(self):
		project = create_test_construction_project()
		stage = create_test_project_stage(
			project=project.name, progress=50, weight=1, status="Em andamento"
		)
		sync_project_physical_progress(project.name)
		self.assertEqual(frappe.db.get_value("Construction Project", project.name, "physical_progress"), 50)

		stage.progress = 80
		stage.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Construction Project", project.name, "physical_progress"), 80)

	def test_weight_sum_warning_on_validate(self):
		"""Obra com etapas cujos pesos != 100% não deve lançar exceção no validate."""
		project = create_test_construction_project()
		create_test_project_stage(project=project.name, weight=10)
		create_test_project_stage(project=project.name, weight=10)
		project.reload()
		project.save()
