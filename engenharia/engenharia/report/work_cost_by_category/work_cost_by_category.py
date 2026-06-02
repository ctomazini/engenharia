import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = [
		{"fieldname": "cost_category", "label": _("Categoria"), "fieldtype": "Link", "options": "Cost Category", "width": 180},
		{"fieldname": "category_name", "label": _("Nome"), "fieldtype": "Data", "width": 200},
		{"fieldname": "total_cost", "label": _("Custo Total"), "fieldtype": "Currency", "width": 140},
	]
	rows = frappe.get_all(
		"Work Cost",
		filters={"status": ["!=", "Cancelado"]},
		fields=["cost_category", "amount"],
		limit=0,
	)
	agg = {}
	for row in rows:
		key = row.cost_category or _("Sem categoria")
		agg[key] = agg.get(key, 0) + flt(row.amount)

	category_names = {
		c.name: c.category_name
		for c in frappe.get_all("Cost Category", fields=["name", "category_name"], limit=0)
	}
	data = [
		{
			"cost_category": key if key != _("Sem categoria") else None,
			"category_name": category_names.get(key, key),
			"total_cost": value,
		}
		for key, value in sorted(agg.items(), key=lambda item: item[1], reverse=True)
	]
	return columns, data
