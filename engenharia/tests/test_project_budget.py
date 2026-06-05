import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt

from engenharia.engenharia.doctype.construction_project.construction_project import create_budget_revision
from engenharia.project_rollup import recompute_construction_project_specs
from engenharia.tests.test_project_item import (
	create_test_technical_item_cylinder,
	create_test_technical_item_unit_sale,
)
from engenharia.tests.test_setup import create_test_construction_project, create_test_supplier


class TestProjectBudget(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _cylinder_outputs(self):
		return [
			{
				"output_key": "volume",
				"label": "Volume",
				"unit": "m³",
				"formula": "pi*(diameter/2)**2*height",
				"sort_order": 1,
				"role": "volume",
			},
			{
				"output_key": "total",
				"label": "Total",
				"unit": "R$",
				"formula": "quantity*volume*unit_price",
				"sort_order": 2,
				"role": "value",
			},
		]

	def test_formula_mode_bdi_on_formula_total(self):
		item = create_test_technical_item_cylinder(outputs=self._cylinder_outputs())
		project = create_test_construction_project()
		doc = frappe.get_doc(
			{
				"doctype": "Project Item",
				"project": project.name,
				"technical_item": item.name,
				"pricing_mode": "Fórmula",
				"bdi_percent": 10,
				"parameter_values": [
					{"field_key": "diameter", "label": "Diâmetro", "data_type": "Número", "value": "2"},
					{"field_key": "height", "label": "Altura", "data_type": "Número", "value": "1"},
					{"field_key": "unit_price", "label": "Preço", "data_type": "Número", "value": "10"},
				],
			}
		)
		doc.insert(ignore_permissions=True)

		self.assertAlmostEqual(doc.direct_cost, 31.4159, places=2)
		self.assertAlmostEqual(doc.total_value, doc.direct_cost * 1.1, places=2)

	def test_composition_mode_components_and_bdi(self):
		item = create_test_technical_item_unit_sale()
		project = create_test_construction_project()
		supplier = create_test_supplier().name

		doc = frappe.get_doc(
			{
				"doctype": "Project Item",
				"project": project.name,
				"technical_item": item.name,
				"pricing_mode": "Composição de custos",
				"quantity": 2,
				"bdi_percent": 20,
				"parameter_values": [
					{
						"field_key": "unit_price",
						"label": "Preço unitário",
						"data_type": "Número",
						"value": "100",
					},
				],
				"cost_components": [
					{
						"description": "Material A",
						"supplier": supplier,
						"quantity": 3,
						"unit": "un",
						"unit_cost": 100,
					},
					{
						"description": "Mão de obra",
						"quantity": 1,
						"unit": "h",
						"unit_cost": 200,
					},
				],
			}
		)
		doc.insert(ignore_permissions=True)

		self.assertAlmostEqual(doc.direct_cost, 500, places=2)
		self.assertAlmostEqual(doc.total_value, 600, places=2)

	def test_composition_mode_unit_price_fallback_with_bdi(self):
		item = create_test_technical_item_unit_sale()
		project = create_test_construction_project()

		doc = frappe.get_doc(
			{
				"doctype": "Project Item",
				"project": project.name,
				"technical_item": item.name,
				"pricing_mode": "Composição de custos",
				"quantity": 3,
				"unit_price": 100,
				"bdi_percent": 20,
				"parameter_values": [
					{
						"field_key": "unit_price",
						"label": "Preço unitário",
						"data_type": "Número",
						"value": "100",
					},
				],
			}
		)
		doc.insert(ignore_permissions=True)

		self.assertAlmostEqual(doc.direct_cost, 300, places=2)
		self.assertAlmostEqual(doc.total_value, 360, places=2)

	def test_rollup_respects_budget_revision(self):
		item = create_test_technical_item_unit_sale()
		project = create_test_construction_project()

		rev1_item = frappe.get_doc(
			{
				"doctype": "Project Item",
				"project": project.name,
				"technical_item": item.name,
				"budget_revision": 1,
				"parameter_values": [
					{
						"field_key": "unit_price",
						"label": "Preço unitário",
						"data_type": "Número",
						"value": "100",
					},
				],
			}
		).insert(ignore_permissions=True)

		rev2_item = frappe.get_doc(
			{
				"doctype": "Project Item",
				"project": project.name,
				"technical_item": item.name,
				"budget_revision": 2,
				"quantity": 1,
				"parameter_values": [
					{
						"field_key": "unit_price",
						"label": "Preço unitário",
						"data_type": "Número",
						"value": "50",
					},
				],
			}
		).insert(ignore_permissions=True)

		frappe.db.set_value("Construction Project", project.name, "budget_revision", 2)
		recompute_construction_project_specs(project.name)
		project.reload()

		self.assertAlmostEqual(project.spec_project_total, rev2_item.total_value, places=2)
		self.assertNotAlmostEqual(project.spec_project_total, rev1_item.total_value, places=2)

	def test_create_budget_revision_increments_and_snapshots(self):
		item = create_test_technical_item_unit_sale()
		project = create_test_construction_project()

		frappe.get_doc(
			{
				"doctype": "Project Item",
				"project": project.name,
				"technical_item": item.name,
				"parameter_values": [
					{
						"field_key": "unit_price",
						"label": "Preço unitário",
						"data_type": "Número",
						"value": "200",
					},
				],
			}
		).insert(ignore_permissions=True)

		recompute_construction_project_specs(project.name)
		project.reload()
		self.assertEqual(project.budget_revision, 1)
		self.assertAlmostEqual(project.spec_project_total, 200, places=2)

		result = create_budget_revision(project.name)
		project.reload()

		self.assertEqual(result["revision_number"], 2)
		self.assertEqual(project.budget_revision, 2)

		vigente_rows = [row for row in project.budget_revisions if row.status == "Vigente"]
		superseded_rows = [row for row in project.budget_revisions if row.status == "Supersedida"]

		self.assertEqual(len(vigente_rows), 1)
		self.assertEqual(vigente_rows[0].revision_number, 2)
		self.assertEqual(flt(vigente_rows[0].total_amount), 0)

		self.assertEqual(len(superseded_rows), 1)
		self.assertEqual(superseded_rows[0].revision_number, 1)
		self.assertAlmostEqual(superseded_rows[0].total_amount, 200, places=2)

	def test_project_item_inherits_default_bdi_on_insert(self):
		item = create_test_technical_item_unit_sale()
		project = create_test_construction_project(default_bdi_percent=15)

		doc = frappe.get_doc(
			{
				"doctype": "Project Item",
				"project": project.name,
				"technical_item": item.name,
				"parameter_values": [
					{
						"field_key": "unit_price",
						"label": "Preço unitário",
						"data_type": "Número",
						"value": "100",
					},
				],
			}
		).insert(ignore_permissions=True)

		self.assertEqual(flt(doc.bdi_percent), 15)
		self.assertAlmostEqual(doc.direct_cost, 100, places=2)
		self.assertAlmostEqual(doc.total_value, 115, places=2)
