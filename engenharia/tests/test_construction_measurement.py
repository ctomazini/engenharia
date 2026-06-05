import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt

from engenharia.tests.test_setup import (
	create_test_construction_measurement,
	create_test_construction_project,
	create_test_project_stage,
)


class TestConstructionMeasurement(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_crud_and_totals(self):
		project = create_test_construction_project()
		stage = create_test_project_stage(
			project=project.name, progress=20, stage_value=10000, status="Em andamento"
		)
		measurement = create_test_construction_measurement(project=project.name, stage=stage.name)
		self.assertTrue(measurement.name.startswith("MED-"))
		self.assertEqual(measurement.customer, project.customer)
		self.assertAlmostEqual(flt(measurement.total_measured_value), 3000, places=2)

	def test_approval_updates_stage_progress(self):
		project = create_test_construction_project()
		stage = create_test_project_stage(
			project=project.name, progress=10, stage_value=5000, status="Em andamento"
		)
		measurement = create_test_construction_measurement(
			project=project.name,
			stage=stage.name,
			measurement_items=[{"project_stage": stage.name, "current_pct": 60}],
		)
		measurement.status = "Aprovada"
		measurement.save(ignore_permissions=True)

		self.assertEqual(flt(frappe.db.get_value("Project Stage", stage.name, "progress")), 60)
		self.assertEqual(
			flt(frappe.db.get_value("Construction Project", project.name, "physical_progress")), 60
		)
