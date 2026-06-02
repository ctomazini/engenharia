import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import (
	create_test_cost_category,
	create_test_project_stage,
	create_test_supplier,
	create_test_work_cost,
	create_test_construction_project,
)


class TestProjectStage(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_crud(self):
		stage = create_test_project_stage(status="Em andamento", progress=50)
		self.assertEqual(stage.status, "Em andamento")
		stage.progress = 100
		stage.status = "Concluída"
		stage.save(ignore_permissions=True)
		name = stage.name
		stage.delete(ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Project Stage", name))
