import os

import frappe

SIDEBAR_LINK_ORDER = (
	("Painel", "eng-dashboard", "Page"),
	("Prazos", "Deadline", "DocType"),
	("Tarefas", "Task", "DocType"),
	("Comunicações", "Communication Log", "DocType"),
	("Registro de Horas", "Time Log", "DocType"),
	("Obras", "Construction Project", "DocType"),
	("Itens na Obra", "Project Item", "DocType"),
	("Clientes", "Customer", "DocType"),
	("Custos de Obra", "Work Cost", "DocType"),
	("Despesas Reembolsáveis", "Reimbursable Expense", "DocType"),
	("Etapas", "Project Stage", "DocType"),
	("Protocolos", "Permit", "DocType"),
	("Contratos", "Engineering Contract", "DocType"),
	("Pagamentos", "Payment", "DocType"),
	("Custo por Obra", "work_cost_by_project", "Report"),
	("Custo por Categoria", "work_cost_by_category", "Report"),
	("Fluxo de Caixa", "cash_flow", "Report"),
	("Obras por Status", "projects_by_status", "Report"),
	("Margem por Obra", "project_margin", "Report"),
	("Fornecedores", "Supplier", "DocType"),
	("Categorias de Custo", "Cost Category", "DocType"),
	("Tipos de Etapa", "Stage Type", "DocType"),
	("Órgãos Públicos", "Public Agency", "DocType"),
	("Itens Técnicos", "Technical Item", "DocType"),
)

SIDEBAR_SECTIONS = (
	{"label": "Dia a Dia", "collapsible": 1, "keep_closed": 0},
	{"label": "Gestão de Obras", "collapsible": 1, "keep_closed": 0},
	{"label": "Financeiro", "collapsible": 1, "keep_closed": 0},
	{"label": "Relatórios", "collapsible": 1, "keep_closed": 1},
	{"label": "Cadastros", "collapsible": 1, "keep_closed": 1},
)


def ensure_engenharia_sidebar():
	"""Garante Workspace Sidebar e Desktop Icon do app (sync idempotente)."""
	_remove_legacy_dashboard_page()

	for folder, filename in (
		("workspace_sidebar", "engenharia.json"),
		("desktop_icon", "engenharia.json"),
	):
		path = frappe.get_app_path("engenharia", folder, filename)
		if os.path.exists(path):
			frappe.import_doc(path)

	frappe.clear_cache()
	frappe.db.commit()  # setup: sincroniza sidebar/desktop icon no migrate


def _remove_legacy_dashboard_page():
	"""Remove Page 'dashboard' — slug conflita com DocType nativo Dashboard do Frappe."""
	if frappe.db.exists("Page", "dashboard"):
		frappe.delete_doc(
			"Page",
			"dashboard",
			force=1,
			ignore_permissions=True,  # setup: remove Page obsoleta no migrate
		)
