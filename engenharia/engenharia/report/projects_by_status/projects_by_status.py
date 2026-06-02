import frappe
from frappe import _


def execute(filters=None):
	columns = [
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 140},
		{"fieldname": "count", "label": _("Quantidade"), "fieldtype": "Int", "width": 120},
	]
	statuses = ["Orçamento", "Em andamento", "Paralisada", "Concluída", "Cancelada"]
	data = []
	for status in statuses:
		data.append({"status": status, "count": frappe.db.count("Construction Project", {"status": status})})
	return columns, data
