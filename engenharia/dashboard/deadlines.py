import frappe
from frappe.utils import add_days, date_diff

from engenharia.dashboard._helpers import (
	LIST_LIMIT_MAX,
	_customer_name_lookup,
	_project_lookup,
)


def build_alerts(hoje, period_end):
	alertas = []
	rows = frappe.get_all(
		"Deadline",
		filters={
			"status": "Pendente",
			"due_date": ["between", [hoje, add_days(hoje, 1)]],
		},
		fields=["name", "description", "due_date", "customer", "project", "priority"],
		order_by="due_date asc",
		limit=20,
	)
	customer_map = _customer_name_lookup([r.customer for r in rows if r.customer])
	for row in rows:
		dias = date_diff(row.due_date, hoje)
		alertas.append(
			{
				"type": "deadline",
				"level": "red" if dias <= 0 else "yellow",
				"title": row.description or row.name,
				"date": row.due_date,
				"customer_name": customer_map.get(row.customer, row.customer or ""),
				"doctype": "Deadline",
				"docname": row.name,
			}
		)

	expiring_permits = frappe.get_all(
		"Permit",
		filters={
			"status": ["in", ["Pendente", "Em análise", "Aprovado"]],
			"expiry_date": ["between", [hoje, period_end]],
		},
		fields=["name", "permit_type", "expiry_date", "project", "customer"],
		order_by="expiry_date asc",
		limit=20,
	)
	project_map = _project_lookup([p.project for p in expiring_permits if p.project])
	for row in expiring_permits:
		alertas.append(
			{
				"type": "permit",
				"level": "orange",
				"title": row.permit_type or row.name,
				"date": row.expiry_date,
				"customer_name": (project_map.get(row.project) or {}).get("title") or row.project or "",
				"doctype": "Permit",
				"docname": row.name,
			}
		)
	return alertas


def get_deadlines(hoje, period_end, limit):
	rows = frappe.get_all(
		"Deadline",
		filters={"due_date": ["between", [hoje, period_end]]},
		fields=["name", "description", "due_date", "customer", "project", "status", "priority"],
		order_by="due_date asc",
		limit=limit,
	)
	customer_map = _customer_name_lookup([r.customer for r in rows if r.customer])
	for row in rows:
		row["customer_name"] = customer_map.get(row.customer, row.customer or "")
		row["days_remaining"] = date_diff(row.due_date, hoje) if row.due_date else None
	return rows


def build_centro_atencao(hoje, period_end, kpis, financeiro, include_financial=True):
	previsto = (
		financeiro.get("previsto_periodo")
		or financeiro.get("previsto_semana")
		or {
			"count": 0,
			"valor": 0,
		}
	)
	result = {
		"prazos_vencidos": kpis.get("overdue_deadlines") or 0,
		"prazos_proximos_3d": kpis.get("urgent_deadlines") or 0,
		"tarefas_atrasadas": kpis.get("late_tasks") or 0,
		"tarefas_pendentes": kpis.get("open_tasks") or 0,
		"obras_ativas": kpis.get("active_projects") or 0,
		"total_clientes": kpis.get("total_customers") or 0,
	}
	if not include_financial:
		return result

	result.update(
		{
			"parcelas_vencidas": kpis.get("parcelas_vencidas") or {"count": 0, "valor": 0},
			"pagamentos_periodo": previsto,
			"recebimentos_periodo": kpis.get("received_period") or {"count": 0, "valor": 0},
			"contratos_ativos": kpis.get("active_contracts") or 0,
			"taxa_recebimento": kpis.get("taxa_recebimento") or 0,
			"spec_project_total": kpis.get("spec_project_total") or 0,
			"custos_mes": kpis.get("month_costs") or {"count": 0, "amount": 0},
			"a_reembolsar": kpis.get("amount_reimbursable") or {"count": 0, "amount": 0},
		}
	)
	return result
