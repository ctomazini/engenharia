import frappe
from frappe.tests.utils import FrappeTestCase

from engenharia.tests.test_setup import _uid


class TestTechnicalItemFormulas(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _base_item(self, **kwargs):
		return {
			"doctype": "Technical Item",
			"item_name": kwargs.pop("item_name", _uid("Formula Item")),
			"item_key": kwargs.pop("item_key", f"frm_{frappe.generate_hash(length=6)}"),
			"data_type": "Número",
			"category": "Geral",
			"fields": kwargs.pop(
				"fields",
				[
					{
						"field_key": "width",
						"label": "Largura",
						"unit": "m",
						"data_type": "Número",
						"required": 1,
						"sort_order": 1,
					},
				],
			),
			**kwargs,
		}

	def test_invalid_formula_syntax(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				self._base_item(
					outputs=[
						{
							"output_key": "area",
							"label": "Área",
							"unit": "m²",
							"formula": "width **",
							"sort_order": 1,
						},
					]
				)
			).insert(ignore_permissions=True)

	def test_formula_unknown_variable(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				self._base_item(
					outputs=[
						{
							"output_key": "area",
							"label": "Área",
							"unit": "m²",
							"formula": "width * depth",
							"sort_order": 1,
						},
					]
				)
			).insert(ignore_permissions=True)

	def test_valid_formula_passes(self):
		doc = frappe.get_doc(
			self._base_item(
				outputs=[
					{
						"output_key": "area",
						"label": "Área",
						"unit": "m²",
						"formula": "width * width",
						"sort_order": 1,
					},
				]
			)
		)
		doc.insert(ignore_permissions=True)
		self.assertEqual(doc.outputs[0].output_key, "area")

	def test_invalid_output_role(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				self._base_item(
					outputs=[
						{
							"output_key": "area",
							"label": "Área",
							"unit": "m²",
							"formula": "width * width",
							"sort_order": 1,
							"role": "invalid_role",
						},
					]
				)
			).insert(ignore_permissions=True)

	def test_at_most_one_value_role(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				self._base_item(
					outputs=[
						{
							"output_key": "total_a",
							"label": "Total A",
							"unit": "R$",
							"formula": "width",
							"sort_order": 1,
							"role": "value",
						},
						{
							"output_key": "total_b",
							"label": "Total B",
							"unit": "R$",
							"formula": "width",
							"sort_order": 2,
							"role": "value",
						},
					]
				)
			).insert(ignore_permissions=True)

	def test_output_key_collides_with_field(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				self._base_item(
					outputs=[
						{
							"output_key": "width",
							"label": "Duplicado",
							"unit": "m",
							"formula": "width",
							"sort_order": 1,
						},
					]
				)
			).insert(ignore_permissions=True)
