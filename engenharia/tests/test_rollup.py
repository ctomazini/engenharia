import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt

from engenharia.project_rollup import recompute_construction_project_specs
from engenharia.tests.test_project_item import (
	create_test_technical_item_cylinder,
	create_test_technical_item_unit_sale,
)
from engenharia.tests.test_setup import create_test_construction_project


class TestProjectRollup(FrappeTestCase):
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
			{
				"output_key": "hint",
				"label": "Resumo",
				"unit": "m³",
				"formula": "volume",
				"sort_order": 3,
				"role": "preview",
			},
		]

	def test_project_total_and_preview(self):
		item = create_test_technical_item_cylinder(outputs=self._cylinder_outputs())
		project = create_test_construction_project()
		doc = frappe.get_doc(
			{
				"doctype": "Project Item",
				"project": project.name,
				"technical_item": item.name,
				"parameter_values": [
					{"field_key": "diameter", "label": "Diâmetro", "data_type": "Número", "value": "2"},
					{"field_key": "height", "label": "Altura", "data_type": "Número", "value": "1"},
					{"field_key": "unit_price", "label": "Preço", "data_type": "Número", "value": "10"},
				],
			}
		)
		doc.insert(ignore_permissions=True)

		recompute_construction_project_specs(project.name)
		project.reload()
		self.assertAlmostEqual(project.spec_project_total, doc.total_value, places=4)

		from engenharia.project_rollup import build_spec_preview_html

		preview = build_spec_preview_html(project.name)
		self.assertIn("Resumo", preview)
		self.assertIn("3.14", preview)

	def test_item_project_total_parity_two_items(self):
		cylinder = create_test_technical_item_cylinder(outputs=self._cylinder_outputs())
		sale = create_test_technical_item_unit_sale()
		project = create_test_construction_project()

		item_a = frappe.get_doc(
			{
				"doctype": "Project Item",
				"project": project.name,
				"technical_item": cylinder.name,
				"quantity": 2,
				"parameter_values": [
					{"field_key": "diameter", "label": "Diâmetro", "data_type": "Número", "value": "2"},
					{"field_key": "height", "label": "Altura", "data_type": "Número", "value": "1"},
					{"field_key": "unit_price", "label": "Preço", "data_type": "Número", "value": "10"},
				],
			}
		).insert(ignore_permissions=True)

		item_b = frappe.get_doc(
			{
				"doctype": "Project Item",
				"project": project.name,
				"technical_item": sale.name,
				"quantity": 3,
				"parameter_values": [
					{
						"field_key": "unit_price",
						"label": "Preço unitário",
						"data_type": "Número",
						"value": "20",
					},
				],
			}
		).insert(ignore_permissions=True)

		recompute_construction_project_specs(project.name)
		project.reload()

		items_total = flt(item_a.total_value) + flt(item_b.total_value)
		self.assertAlmostEqual(project.spec_project_total, items_total, places=4)
		self.assertAlmostEqual(item_a.total_value, item_a.computed_outputs[1].value, places=4)
		self.assertAlmostEqual(item_b.total_value, item_b.computed_outputs[0].value, places=4)
