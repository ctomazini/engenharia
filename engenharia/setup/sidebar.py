import os

import frappe

# Ordem canônica da sidebar Engenharia (espelha workspace_sidebar/engenharia.json).
# Seções: Dia a Dia | Obras | Orçamento | Receitas | Despesas | Relatórios | Cadastros | Administração
SIDEBAR_LINK_ORDER = (
	# Dia a Dia
	("Painel", "eng-dashboard", "Page"),
	("Prazos", "Deadline", "DocType"),
	("Tarefas", "Task", "DocType"),
	("Comunicações", "Communication Log", "DocType"),
	("Registro de Horas", "Time Log", "DocType"),
	# Obras
	("Obras", "Construction Project", "DocType"),
	("Etapas", "Project Stage", "DocType"),
	("Boletins de Medição", "Construction Measurement", "DocType"),
	("Protocolos", "Permit", "DocType"),
	# Orçamento
	("Itens do Projeto", "Project Item", "DocType"),
	("Itens Técnicos", "Technical Item", "DocType"),
	# Receitas
	("Contratos de Honorários", "Engineering Contract", "DocType"),
	("Recebimentos", "Payment", "DocType"),
	("Comissões", "Commission", "DocType"),
	# Despesas
	("Compras e NF Avulsas", "Work Cost", "DocType"),
	("Subcontratos", "Subcontract", "DocType"),
	("Despesas Reembolsáveis", "Reimbursable Expense", "DocType"),
	("Custos Realizados", "consolidated_cost", "Report"),
	# Relatórios
	("Visão de Custos Realizados", "consolidated_cost", "Report"),
	("Orçado vs Realizado", "budget_vs_actual", "Report"),
	("Compras avulsas por obra", "work_cost_by_project", "Report"),
	("Compras avulsas por categoria", "work_cost_by_category", "Report"),
	("Fluxo de Caixa", "cash_flow", "Report"),
	("Margem por Obra", "project_margin", "Report"),
	("Obras por Status", "projects_by_status", "Report"),
	# Cadastros
	("Clientes", "Customer", "DocType"),
	("Fornecedores", "Supplier", "DocType"),
	("Classificações de Gasto", "Cost Category", "DocType"),
	("Tipos de Etapa", "Stage Type", "DocType"),
	("Órgãos Públicos", "Public Agency", "DocType"),
	("Templates de Documento", "Document Template", "DocType"),
	("Kits de Documentos", "Document Kit", "DocType"),
	("Modelos de Etapas", "Project Stage Template", "DocType"),
	# Administração
	("Configurações do Escritório", "Engineering Settings", "DocType"),
	("Usuários", "User", "DocType"),
	("Novo Usuário", "/app/user/new", "URL"),
)

SIDEBAR_SECTIONS = (
	# Frappe v16: Section Break com filhos exige collapsible=1, senão toggle() quebra
	# ao fechar a sidebar (evento sidebar-expand) e o scroll do desk trava.
	{"label": "Dia a Dia", "collapsible": 1, "keep_closed": 0},
	{"label": "Obras", "collapsible": 1, "keep_closed": 0},
	{"label": "Orçamento", "collapsible": 1, "keep_closed": 1},
	{"label": "Receitas", "collapsible": 1, "keep_closed": 1},
	{"label": "Despesas", "collapsible": 1, "keep_closed": 1},
	{"label": "Relatórios", "collapsible": 1, "keep_closed": 1},
	{"label": "Cadastros", "collapsible": 1, "keep_closed": 1},
	{"label": "Administração", "collapsible": 1, "keep_closed": 1},
)


def _validate_section_break_collapsible():
	"""Section Break com filhos deve ter collapsible=1 (requisito do Frappe v16 sidebar JS)."""
	if not frappe.db.exists("Workspace Sidebar", "Engenharia"):
		return

	sections = frappe.get_all(
		"Workspace Sidebar Item",
		filters={"parent": "Engenharia", "type": "Section Break"},
		fields=["label", "collapsible", "idx"],
		order_by="idx asc",
	)
	links = frappe.get_all(
		"Workspace Sidebar Item",
		filters={"parent": "Engenharia", "type": "Link"},
		fields=["idx"],
		order_by="idx asc",
	)
	link_idxs = [row.idx for row in links]

	for section in sections:
		has_children = any(idx > section.idx for idx in link_idxs)
		if has_children and not section.collapsible:
			frappe.log_error(
				title="Engenharia sidebar: Section Break sem collapsible",
				message=(
					f'Seção "{section.label}" tem itens filhos mas collapsible=0; '
					"isso quebra Sidebar.close() no desk (toggle sem $drop_icon)."
				),
			)


def _validate_sidebar_links():
	"""Garante que o JSON importado mantém os links na ordem esperada."""
	if not frappe.db.exists("Workspace Sidebar", "Engenharia"):
		return

	links = frappe.get_all(
		"Workspace Sidebar Item",
		filters={"parent": "Engenharia", "type": "Link"},
		fields=["label", "link_to", "link_type", "url", "idx"],
		order_by="idx asc",
	)

	if len(links) != len(SIDEBAR_LINK_ORDER):
		frappe.log_error(
			title="Engenharia sidebar: contagem de links divergente",
			message=f"Esperado {len(SIDEBAR_LINK_ORDER)}, encontrado {len(links)}",
		)
		return

	for idx, (expected, link) in enumerate(zip(SIDEBAR_LINK_ORDER, links, strict=True)):
		label, link_to, link_type = expected
		actual_link_to = link.url if link_type == "URL" else link.link_to
		if (
			link.label != label
			or actual_link_to != link_to
			or link.link_type != link_type
		):
			frappe.log_error(
				title="Engenharia sidebar: ordem divergente",
				message=(
					f"Posição {idx + 1}: esperado {label}/{link_to}/{link_type}, "
					f"encontrado {link.label}/{actual_link_to}/{link.link_type}"
				),
			)
			return


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

	_validate_sidebar_links()
	_validate_section_break_collapsible()
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
