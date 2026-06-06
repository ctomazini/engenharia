import frappe
from frappe.utils import flt, getdate, today

from engenharia.dashboard._helpers import _customer_name_lookup, _project_lookup
from engenharia.titles import get_customer_name

ACTIVE_PROJECT_STATUSES = ("Orçamento", "Em andamento", "Paralisada")


def get_recent_measurements(limit: int = 5) -> list[dict]:
	rows = frappe.get_all(
		"Construction Measurement",
		filters={"status": ["in", ["Rascunho", "Aprovada", "Contestada"]]},
		fields=["name", "title", "project", "reference_period", "measurement_date"],
		order_by="measurement_date desc",
		limit=limit,
	)
	project_map = _project_lookup([row.project for row in rows if row.project])
	for row in rows:
		project = project_map.get(row.project) or {}
		row["project_title"] = project.get("title") or row.project or ""
	return rows


def get_active_projects_enriched(limit: int = 10) -> list[dict]:
	hoje = today()
	projects = frappe.get_all(
		"Construction Project",
		filters={"status": ["in", list(ACTIVE_PROJECT_STATUSES)]},
		fields=[
			"name",
			"title",
			"customer",
			"physical_progress",
			"status",
		],
		order_by="modified desc",
		limit=limit,
	)
	if not projects:
		return []

	project_names = [row.name for row in projects]
	customer_map = _customer_name_lookup([row.customer for row in projects if row.customer])

	deadlines = frappe.get_all(
		"Deadline",
		filters={
			"project": ["in", project_names],
			"status": "Pendente",
		},
		fields=["project", "description", "due_date"],
		order_by="due_date asc",
		limit=500,
	)
	next_deadline_by_project: dict[str, dict] = {}
	for row in deadlines:
		if row.project not in next_deadline_by_project:
			next_deadline_by_project[row.project] = row

	result = []
	for project in projects:
		deadline = next_deadline_by_project.get(project.name)
		customer_name = customer_map.get(project.customer) or get_customer_name(project.customer)
		short_customer = customer_name.split(" ")[0] if customer_name else ""
		if customer_name and len(customer_name.split()) > 1:
			short_customer = f"{customer_name.split()[0]} {customer_name.split()[1][0]}."

		due_label = ""
		is_overdue = False
		if deadline:
			due_label = f"{frappe.utils.formatdate(deadline.due_date, 'dd/MM')} — {deadline.description}"
			is_overdue = getdate(deadline.due_date) < getdate(hoje)

		result.append(
			{
				"name": project.name,
				"title": project.title or project.name,
				"customer_name": customer_name,
				"customer_short": short_customer,
				"physical_progress": flt(project.physical_progress),
				"status": project.status,
				"next_deadline": due_label,
				"next_deadline_overdue": is_overdue,
			}
		)

	return result
