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

DEFAULT_TECHNICAL_ITEMS = (
	{
		"item_name": "Fossa séptica",
		"item_key": "fossa_septica",
		"category": "Hidráulica",
		"data_type": "Número",
		"fields": (
			{"field_key": "useful_height", "label": "Altura útil", "unit": "m", "data_type": "Número", "required": 1, "sort_order": 1},
			{"field_key": "useful_width", "label": "Largura útil", "unit": "m", "data_type": "Número", "required": 1, "sort_order": 2},
			{"field_key": "total_height", "label": "Altura total", "unit": "m", "data_type": "Número", "required": 0, "sort_order": 3},
			{"field_key": "total_width", "label": "Largura total", "unit": "m", "data_type": "Número", "required": 0, "sort_order": 4},
			{"field_key": "volume_m3", "label": "Volume", "unit": "m³", "data_type": "Número", "required": 1, "sort_order": 5},
			{"field_key": "volume_l", "label": "Volume", "unit": "L", "data_type": "Número", "required": 1, "sort_order": 6},
		),
		"outputs": (
			{
				"output_key": "volume",
				"label": "Área útil",
				"unit": "m²",
				"formula": "useful_height * useful_width",
				"sort_order": 1,
				"role": "volume",
			},
		),
	},
	{
		"item_name": "Caixa d'água",
		"item_key": "caixa_dagua",
		"category": "Hidráulica",
		"data_type": "Número",
		"fields": (
			{"field_key": "reservation_l", "label": "Reservação", "unit": "L", "data_type": "Número", "required": 1, "sort_order": 1},
			{"field_key": "material", "label": "Material", "unit": "", "data_type": "Texto", "required": 0, "sort_order": 2},
			{"field_key": "quantity", "label": "Quantidade", "unit": "un", "data_type": "Número", "required": 0, "sort_order": 3},
		),
	},
	{
		"item_name": "Área de piso",
		"item_key": "area_piso",
		"category": "Estrutural",
		"data_type": "Número",
		"fields": (
			{"field_key": "floor_level", "label": "Pavimento", "unit": "", "data_type": "Texto", "required": 1, "sort_order": 1},
			{"field_key": "area_m2", "label": "Área", "unit": "m²", "data_type": "Número", "required": 1, "sort_order": 2},
			{"field_key": "usage", "label": "Uso", "unit": "", "data_type": "Texto", "required": 0, "sort_order": 3},
		),
	},
	{
		"item_name": "Item genérico",
		"item_key": "generic_item",
		"category": "Geral",
		"data_type": "Número",
		"default_unit": "un",
		"fields": (
			{"field_key": "value", "label": "Valor", "unit": "un", "data_type": "Número", "required": 1, "sort_order": 1},
		),
	},
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


def _sync_technical_item_template(item_def: dict) -> None:
	name = item_def["item_name"]
	if not frappe.db.exists("Technical Item", name):
		legacy = frappe.db.get_value("Technical Item", {"item_key": item_def["item_key"]}, "name")
		if legacy and legacy != name:
			frappe.rename_doc("Technical Item", legacy, name, force=True, merge=True)
		doc = frappe.get_doc(
			{
				"doctype": "Technical Item",
				"item_name": item_def["item_name"],
				"item_key": item_def["item_key"],
				"category": item_def["category"],
				"data_type": item_def["data_type"],
				"default_unit": item_def.get("default_unit"),
				"fields": list(item_def["fields"]),
				"outputs": list(item_def.get("outputs") or ()),
			}
		)
		doc.insert(ignore_permissions=True)  # setup: seed idempotente de itens técnicos
		return

	doc = frappe.get_doc("Technical Item", name)
	changed = False
	if len(doc.fields) < len(item_def["fields"]):
		doc.fields = []
		for row in item_def["fields"]:
			doc.append("fields", row)
		changed = True

	template_outputs = list(item_def.get("outputs") or ())
	if template_outputs:
		doc.outputs = []
		for row in template_outputs:
			doc.append("outputs", row)
		changed = True

	if changed:
		doc.save(ignore_permissions=True)  # setup: complementa template existente


def ensure_technical_item_templates():
	for item_def in DEFAULT_TECHNICAL_ITEMS:
		_sync_technical_item_template(item_def)


def ensure_seed_data():
	ensure_default_cost_categories()
	ensure_default_stage_types()
	ensure_engineering_settings()
	ensure_technical_item_templates()
	frappe.db.commit()  # setup: seed idempotente no migrate
