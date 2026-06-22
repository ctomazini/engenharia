import os

import frappe

PRINT_FORMAT_NAMES = (
	"Engenharia - Contrato de Obra",
	"Engenharia - Recibo de Pagamento",
	"Engenharia - Orçamento da Obra",
	"Engenharia - Custos Realizados (Resumo)",
	"Engenharia - Custos Realizados (Detalhado)",
	"Engenharia - Custos Realizados (Paisagem)",
	"Engenharia - Orçado vs Realizado (Resumo)",
	"Engenharia - Orçado vs Realizado (Paisagem)",
	"Engenharia - Fluxo de Caixa (Resumo)",
	"Engenharia - Fluxo de Caixa (Paisagem)",
	"Engenharia - Compras avulsas por obra (Resumo)",
	"Engenharia - Compras avulsas por categoria (Resumo)",
	"Engenharia - Margem por Obra (Resumo)",
	"Engenharia - Margem por Obra (Paisagem)",
)

_DOCTYPE_PRINT_FORMATS = (
	{
		"name": "Engenharia - Contrato de Obra",
		"doc_type": "Engineering Contract",
		"html_file": "contrato.html",
	},
	{
		"name": "Engenharia - Recibo de Pagamento",
		"doc_type": "Payment",
		"html_file": "recibo.html",
	},
	{
		"name": "Engenharia - Orçamento da Obra",
		"doc_type": "Construction Project",
		"html_file": "orcamento.html",
	},
)

_REPORT_PRINT_FORMATS = (
	{
		"name": "Engenharia - Custos Realizados (Resumo)",
		"report": "consolidated_cost",
		"parts": ("reports/_header.html", "reports/_table_consolidated_resumo.html", "reports/_footer.html"),
	},
	{
		"name": "Engenharia - Custos Realizados (Detalhado)",
		"report": "consolidated_cost",
		"parts": ("reports/_header.html", "reports/_table_consolidated_detalhe.html", "reports/_footer.html"),
	},
	{
		"name": "Engenharia - Custos Realizados (Paisagem)",
		"report": "consolidated_cost",
		"parts": (
			"reports/_header.html",
			"reports/_table_consolidated_detalhe.html",
			"reports/_footer.html",
		),
		"landscape": True,
	},
	{
		"name": "Engenharia - Orçado vs Realizado (Resumo)",
		"report": "budget_vs_actual",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
	},
	{
		"name": "Engenharia - Orçado vs Realizado (Paisagem)",
		"report": "budget_vs_actual",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
		"landscape": True,
	},
	{
		"name": "Engenharia - Fluxo de Caixa (Resumo)",
		"report": "cash_flow",
		"parts": ("reports/_header.html", "reports/_table_cash_flow_resumo.html", "reports/_footer.html"),
	},
	{
		"name": "Engenharia - Fluxo de Caixa (Paisagem)",
		"report": "cash_flow",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
		"landscape": True,
	},
	{
		"name": "Engenharia - Compras avulsas por obra (Resumo)",
		"report": "work_cost_by_project",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
	},
	{
		"name": "Engenharia - Compras avulsas por categoria (Resumo)",
		"report": "work_cost_by_category",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
	},
	{
		"name": "Engenharia - Margem por Obra (Resumo)",
		"report": "project_margin",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
	},
	{
		"name": "Engenharia - Margem por Obra (Paisagem)",
		"report": "project_margin",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
		"landscape": True,
	},
)

_DOCTYPE_SYNC_FIELDS = (
	"print_format_for",
	"doc_type",
	"module",
	"standard",
	"custom_format",
	"print_format_type",
	"disabled",
	"html",
)

_REPORT_SYNC_FIELDS = (
	"print_format_for",
	"report",
	"module",
	"standard",
	"custom_format",
	"print_format_type",
	"disabled",
	"html",
	"css",
)


def _load_html(filename):
	base = frappe.get_app_path("engenharia", "print_formats")
	path = os.path.join(base, filename)
	with open(path, encoding="utf-8") as f:
		return f.read()


def _compose_report_html(parts, landscape=False):
	sections = [_load_html("reports/_styles.html")]
	if landscape:
		sections.append(_load_html("reports/_landscape.css"))
	for part in parts:
		sections.append(_load_html(part))
	return "\n".join(sections)


def _sync_doctype_print_format(spec):
	html = _load_html(spec["html_file"])
	values = {
		"print_format_for": "DocType",
		"doc_type": spec["doc_type"],
		"module": "Engenharia",
		"standard": "No",
		"custom_format": 1,
		"print_format_type": "Jinja",
		"disabled": 0,
		"html": html,
	}

	if frappe.db.exists("Print Format", spec["name"]):
		doc = frappe.get_doc("Print Format", spec["name"])
		for field in _DOCTYPE_SYNC_FIELDS:
			doc.set(field, values[field])
		doc.save(ignore_permissions=True)  # setup: sincroniza print formats do app
	else:
		doc = frappe.get_doc({"doctype": "Print Format", "name": spec["name"], **values})
		doc.insert(ignore_permissions=True)  # setup: sincroniza print formats do app


def _sync_report_print_format(spec):
	html = _compose_report_html(spec.get("parts") or (), spec.get("landscape"))
	values = {
		"print_format_for": "Report",
		"report": spec["report"],
		"module": "Engenharia",
		"standard": "No",
		"custom_format": 1,
		"print_format_type": "JS",
		"disabled": 0,
		"html": html,
		"css": None,
	}

	if frappe.db.exists("Print Format", spec["name"]):
		doc = frappe.get_doc("Print Format", spec["name"])
		for field in _REPORT_SYNC_FIELDS:
			doc.set(field, values[field])
		doc.save(ignore_permissions=True)  # setup: sincroniza print formats do app
	else:
		doc = frappe.get_doc({"doctype": "Print Format", "name": spec["name"], **values})
		doc.insert(ignore_permissions=True)  # setup: sincroniza print formats do app


def ensure_engenharia_print_formats():
	"""Sincroniza Print Formats do app (idempotente)."""
	for spec in _DOCTYPE_PRINT_FORMATS:
		_sync_doctype_print_format(spec)
	for spec in _REPORT_PRINT_FORMATS:
		_sync_report_print_format(spec)

	frappe.clear_cache()
	frappe.db.commit()  # setup: sincroniza print formats no migrate
