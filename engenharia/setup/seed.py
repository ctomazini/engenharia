import frappe

DEFAULT_COST_CATEGORIES = (
	"Material",
	"Mão de obra",
	"Equipamentos",
	"Serviços terceirizados",
	"Administrativo",
)

DEFAULT_STAGE_TYPES = (
	("Projeto", 1),
	("Fundação", 2),
	("Estrutura", 3),
	("Alvenaria", 4),
	("Instalações", 5),
	("Acabamento", 6),
	("Entrega", 7),
)


def ensure_default_cost_categories():
	for name in DEFAULT_COST_CATEGORIES:
		if frappe.db.exists("Cost Category", name):
			continue
		frappe.get_doc({"doctype": "Cost Category", "category_name": name}).insert(
			ignore_permissions=True  # setup: seed idempotente de categorias
		)


def ensure_default_stage_types():
	for stage_name, order in DEFAULT_STAGE_TYPES:
		if frappe.db.exists("Stage Type", stage_name):
			continue
		frappe.get_doc(
			{
				"doctype": "Stage Type",
				"stage_name": stage_name,
				"default_order": order,
			}
		).insert(ignore_permissions=True)  # setup: seed idempotente de tipos de etapa


def ensure_engineering_settings():
	if frappe.db.exists("Engineering Settings", "Engineering Settings"):
		return
	doc = frappe.get_doc(
		{
			"doctype": "Engineering Settings",
			"company_name": "Escritório de Engenharia",
		}
	)
	doc.insert(ignore_permissions=True)  # setup: seed do Single de configuração


def ensure_seed_data():
	ensure_default_cost_categories()
	ensure_default_stage_types()
	ensure_engineering_settings()
	frappe.db.commit()  # setup: seed idempotente no migrate
