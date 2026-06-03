import math

import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.engenharia.doctype.construction_project.construction_project import create_project_item
from engenharia.tests.test_setup import _uid, create_test_construction_project


def create_test_technical_item_cylinder(**kwargs):
	fields = kwargs.pop(
		"fields",
		[
			{
				"field_key": "diameter",
				"label": "Diâmetro",
				"unit": "m",
				"data_type": "Número",
				"required": 1,
				"sort_order": 1,
			},
			{
				"field_key": "height",
				"label": "Altura",
				"unit": "m",
				"data_type": "Número",
				"required": 1,
				"sort_order": 2,
			},
			{
				"field_key": "unit_price",
				"label": "Preço unitário",
				"unit": "R$",
				"data_type": "Número",
				"required": 0,
				"sort_order": 3,
				"default_value": "100",
			},
		],
	)
	outputs = kwargs.pop(
		"outputs",
		[
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
				"formula": "volume*unit_price",
				"sort_order": 2,
				"role": "value",
			},
		],
	)
	doc = frappe.get_doc(
		{
			"doctype": "Technical Item",
			"item_name": kwargs.pop("item_name", _uid("Cilindro")),
			"item_key": kwargs.pop("item_key", f"cyl_{frappe.generate_hash(length=6)}"),
			"data_type": "Número",
			"category": "Estrutural",
			"fields": fields,
			"outputs": outputs,
			**kwargs,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_technical_item_unit_sale(**kwargs):
	fields = kwargs.pop(
		"fields",
		[
			{
				"field_key": "unit_price",
				"label": "Preço unitário",
				"unit": "R$",
				"data_type": "Número",
				"required": 1,
				"sort_order": 1,
			},
		],
	)
	outputs = kwargs.pop(
		"outputs",
		[
			{
				"output_key": "line_total",
				"label": "Total da linha",
				"unit": "R$",
				"formula": "quantity*unit_price",
				"sort_order": 1,
				"role": "value",
			},
		],
	)
	doc = frappe.get_doc(
		{
			"doctype": "Technical Item",
			"item_name": kwargs.pop("item_name", _uid("Venda un")),
			"item_key": kwargs.pop("item_key", f"sale_{frappe.generate_hash(length=6)}"),
			"data_type": "Número",
			"category": "Geral",
			"fields": fields,
			"outputs": outputs,
			**kwargs,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


class TestProjectItem(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_cylinder_volume_and_total(self):
		item = create_test_technical_item_cylinder()
		project = create_test_construction_project()
		doc = frappe.get_doc(
			{
				"doctype": "Project Item",
				"project": project.name,
				"technical_item": item.name,
				"quantity": 1,
				"parameter_values": [
					{
						"field_key": "diameter",
						"label": "Diâmetro",
						"data_type": "Número",
						"value": "2",
					},
					{
						"field_key": "height",
						"label": "Altura",
						"data_type": "Número",
						"value": "3",
					},
					{
						"field_key": "unit_price",
						"label": "Preço unitário",
						"data_type": "Número",
						"value": "50",
					},
				],
			}
		)
		doc.insert(ignore_permissions=True)

		expected_volume = math.pi * (1**2) * 3
		outputs = {row.output_key: row.value for row in doc.computed_outputs}
		self.assertAlmostEqual(outputs["volume"], expected_volume, places=4)
		self.assertAlmostEqual(outputs["total"], expected_volume * 50, places=4)
		self.assertAlmostEqual(doc.total_value, expected_volume * 50, places=4)
		self.assertIn("×1", doc.title)

	def test_quantity_unit_price_sale(self):
		item = create_test_technical_item_unit_sale()
		project = create_test_construction_project()
		doc = frappe.get_doc(
			{
				"doctype": "Project Item",
				"project": project.name,
				"technical_item": item.name,
				"quantity": 4,
				"parameter_values": [
					{
						"field_key": "unit_price",
						"label": "Preço unitário",
						"data_type": "Número",
						"required": 1,
						"value": "25",
					},
				],
			}
		)
		doc.insert(ignore_permissions=True)
		self.assertEqual(doc.computed_outputs[0].value, 100)
		self.assertEqual(doc.total_value, 100)

	def test_required_parameter_empty(self):
		item = create_test_technical_item_unit_sale()
		project = create_test_construction_project()
		with self.assertRaises(frappe.ValidationError):
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
							"required": 1,
							"value": "",
						},
					],
				}
			).insert(ignore_permissions=True)

	def test_load_parameters_on_validate_when_empty(self):
		item = create_test_technical_item_cylinder()
		project = create_test_construction_project()
		doc = frappe.get_doc(
			{
				"doctype": "Project Item",
				"project": project.name,
				"technical_item": item.name,
			}
		)
		doc.flags.ignore_required_parameters = True
		doc.insert(ignore_permissions=True)
		self.assertEqual(len(doc.parameter_values), 3)
		self.assertEqual(doc.parameter_values[0].label, "Diâmetro")

	def test_create_project_item_whitelist(self):
		item = create_test_technical_item_cylinder()
		project = create_test_construction_project()
		name = create_project_item(
			project=project.name,
			technical_item=item.name,
			instance_label="Instância teste",
		)
		doc = frappe.get_doc("Project Item", name)
		self.assertEqual(doc.project, project.name)
		self.assertEqual(len(doc.parameter_values), 3)
		self.assertEqual(doc.parameter_values[2].value, "100")
