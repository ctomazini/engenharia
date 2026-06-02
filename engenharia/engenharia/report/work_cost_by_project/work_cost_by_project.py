import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = [
		{"fieldname": "project", "label": _("Obra"), "fieldtype": "Link", "options": "Construction Project", "width": 180},
		{"fieldname": "project_title", "label": _("Título"), "fieldtype": "Data", "width": 220},
		{"fieldname": "total_cost", "label": _("Custo Total"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "entries", "label": _("Lançamentos"), "fieldtype": "Int", "width": 100},
	]
	rows = frappe.get_all(
		"Work Cost",
		filters={"status": ["!=", "Cancelado"]},
		fields=["project", "amount"],
		limit=0,
	)
	agg = {}
	for row in rows:
		bucket = agg.setdefault(row.project, {"total_cost": 0, "entries": 0})
		bucket["total_cost"] += flt(row.amount)
		bucket["entries"] += 1

	project_titles = {
		p.name: p.title
		for p in frappe.get_all("Construction Project", fields=["name", "title"], limit=0)
	}
	data = []
	for project, values in sorted(agg.items(), key=lambda item: item[1]["total_cost"], reverse=True):
		data.append(
			{
				"project": project,
				"project_title": project_titles.get(project, project),
				"total_cost": values["total_cost"],
				"entries": values["entries"],
			}
		)
	return columns, data
