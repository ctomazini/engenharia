import io
import json
import os
import re

import frappe
from frappe import _
from frappe.utils import flt, formatdate, getdate, today

from engenharia.titles import get_customer_name

PLACEHOLDER_REFERENCE = [
	{
		"grupo": "Escritório",
		"items": [
			{"placeholder": "company_name", "label": "Nome do escritório"},
		],
	},
	{
		"grupo": "Cliente",
		"items": [
			{"placeholder": "customer_name", "label": "Nome / Razão Social", "alias": "nome"},
			{"placeholder": "customer_person_type", "label": "Tipo de pessoa"},
			{"placeholder": "customer_cpf", "label": "CPF", "alias": "cpf"},
			{"placeholder": "customer_cnpj", "label": "CNPJ", "alias": "cnpj"},
			{"placeholder": "customer_rg", "label": "RG", "alias": "rg"},
			{"placeholder": "customer_trade_name", "label": "Nome fantasia"},
			{"placeholder": "customer_nationality", "label": "Nacionalidade"},
			{"placeholder": "customer_marital_status", "label": "Estado civil"},
			{"placeholder": "customer_profession", "label": "Profissão"},
			{"placeholder": "customer_legal_representative", "label": "Representante legal"},
		],
	},
	{
		"grupo": "Endereço do cliente",
		"items": [
			{"placeholder": "address_street", "label": "Logradouro", "alias": "endereco"},
			{"placeholder": "address_number", "label": "Número", "alias": "numero"},
			{"placeholder": "address_complement", "label": "Complemento"},
			{"placeholder": "address_district", "label": "Bairro", "alias": "bairro"},
			{"placeholder": "address_city", "label": "Cidade", "alias": "cidade"},
			{"placeholder": "address_state", "label": "UF", "alias": "estado"},
			{"placeholder": "address_cep", "label": "CEP", "alias": "cep"},
			{"placeholder": "address_full", "label": "Endereço completo"},
		],
	},
	{
		"grupo": "Contato",
		"items": [
			{"placeholder": "contact_name", "label": "Nome do contato"},
			{"placeholder": "contact_phone", "label": "Telefone", "alias": "telefone"},
			{"placeholder": "contact_email", "label": "E-mail", "alias": "email"},
		],
	},
	{
		"grupo": "Obra",
		"items": [
			{"placeholder": "project", "label": "Código da obra"},
			{"placeholder": "project_title", "label": "Título da obra", "alias": "titulo_obra"},
			{"placeholder": "project_city", "label": "Cidade da obra"},
			{"placeholder": "project_status", "label": "Status da obra"},
			{"placeholder": "project_type", "label": "Tipo de obra"},
			{"placeholder": "project_address_street", "label": "Logradouro da obra"},
			{"placeholder": "project_address_number", "label": "Número da obra"},
			{"placeholder": "project_address_district", "label": "Bairro da obra"},
			{"placeholder": "project_address_cep", "label": "CEP da obra"},
			{"placeholder": "project_address_full", "label": "Endereço completo da obra"},
			{"placeholder": "project_construction_area", "label": "Área construída (m²)"},
			{"placeholder": "spec_project_total", "label": "Total especificações (R$)"},
		],
	},
	{
		"grupo": "Contrato",
		"condicional": True,
		"items": [
			{"placeholder": "contract_name", "label": "Código do contrato"},
			{"placeholder": "contract_value", "label": "Valor do contrato"},
			{"placeholder": "contract_status", "label": "Status do contrato"},
		],
	},
	{
		"grupo": "Data",
		"items": [
			{"placeholder": "today", "label": "Data de hoje (formatada)"},
			{"placeholder": "today_iso", "label": "Data de hoje (ISO)"},
		],
	},
]


@frappe.whitelist()
def generate_project_documents(project_name: str, template_names) -> dict:
	frappe.has_permission("Construction Project", "write", doc=project_name, throw=True)
	names = _parse_template_names(template_names)
	if not names:
		frappe.throw(_("Selecione ao menos um template."))

	context = _build_context(project_name)
	generated = []
	failures = []

	for template_name in names:
		try:
			template_doc = frappe.get_doc("Document Template", template_name)
			if not template_doc.enabled:
				raise frappe.ValidationError(_("Template desabilitado: {0}").format(template_name))
			result = _render_and_attach(project_name, template_doc, context)
			generated.append(
				{
					"template": template_name,
					"title": template_doc.title,
					"file_name": result["file_name"],
					"file_url": result["file_url"],
				}
			)
		except frappe.ValidationError as exc:
			failures.append({"template": template_name, "error": str(exc)})
		except Exception:
			failures.append({"template": template_name, "error": _("Erro ao gerar documento.")})
			frappe.log_error(
				title=_("Erro ao gerar documento {0}").format(template_name),
				message=frappe.get_traceback(),
			)

	return {"generated": generated, "failures": failures, "total": len(generated)}


@frappe.whitelist()
def get_available_templates() -> list[dict]:
	frappe.has_permission("Document Template", "read", throw=True)
	return frappe.get_all(
		"Document Template",
		filters={"enabled": 1},
		fields=["name", "title", "document_type", "description"],
		order_by="title asc",
		limit_page_length=100,
	)


@frappe.whitelist()
def get_available_kits() -> list[dict]:
	frappe.has_permission("Document Kit", "read", throw=True)

	kits = frappe.get_all(
		"Document Kit",
		fields=["name", "kit_name", "description"],
		filters={"enabled": 1},
		order_by="kit_name asc",
		limit_page_length=100,
	)
	if not kits:
		return kits

	kit_names = [row.name for row in kits]
	item_rows = frappe.get_all(
		"Document Kit Item",
		filters={"parent": ["in", kit_names]},
		fields=["parent", "document_template", "sort_order"],
		order_by="parent asc, sort_order asc, idx asc",
		limit_page_length=500,
	)
	templates_by_kit = {name: [] for name in kit_names}
	for row in item_rows:
		if row.document_template:
			templates_by_kit.setdefault(row.parent, []).append(row.document_template)

	for kit in kits:
		kit["templates"] = templates_by_kit.get(kit.name, [])
	return kits


@frappe.whitelist()
def get_placeholder_reference() -> list[dict]:
	frappe.has_permission("Document Template", "read", throw=True)
	return PLACEHOLDER_REFERENCE


def _parse_template_names(template_names):
	if isinstance(template_names, str):
		template_names = json.loads(template_names or "[]")
	if not isinstance(template_names, list):
		frappe.throw(_("Lista de templates inválida."))
	return [name for name in template_names if name]


def _format_full_address(street, number, complement, district, city, state, cep):
	parts = []
	line = " ".join(part for part in [street or "", number or ""] if part).strip()
	if line:
		parts.append(line)
	if complement:
		parts.append(complement)
	if district:
		parts.append(district)
	city_line = " - ".join(part for part in [city or "", state or ""] if part).strip(" -")
	if city_line:
		parts.append(city_line)
	if cep:
		parts.append(cep)
	return ", ".join(parts)


def _primary_customer_address(customer) -> dict | None:
	if not customer or not customer.addresses:
		return None
	primary = next((row for row in customer.addresses if row.is_primary), None)
	return primary or customer.addresses[0]


def _primary_customer_contact(customer) -> dict | None:
	if not customer or not customer.contacts:
		return None
	return customer.contacts[0]


def _build_context(project_name: str) -> dict:
	project = frappe.get_doc("Construction Project", project_name)
	customer = frappe.get_doc("Customer", project.customer) if project.customer else None
	addr = _primary_customer_address(customer)
	contact = _primary_customer_contact(customer)

	contract_rows = frappe.get_all(
		"Engineering Contract",
		filters={"project": project.name, "status": ["!=", "Cancelado"]},
		fields=["name", "current_value", "status"],
		order_by="modified desc",
		limit_page_length=1,
	)
	contract_row = contract_rows[0] if contract_rows else None

	settings = frappe.get_single("Engineering Settings")
	spec_total = flt(project.spec_project_total)

	project_address_full = _format_full_address(
		project.address_street,
		project.address_number,
		None,
		project.address_district,
		project.city,
		project.address_uf,
		project.address_cep,
	)
	customer_address_full = _format_full_address(
		addr.street if addr else "",
		addr.number if addr else "",
		addr.complement if addr else "",
		addr.district if addr else "",
		addr.city if addr else "",
		addr.state if addr else "",
		addr.cep if addr else "",
	)

	return {
		"company_name": settings.company_name or "",
		"customer_name": get_customer_name(project.customer),
		"nome": get_customer_name(project.customer),
		"customer_person_type": customer.person_type if customer else "",
		"customer_cpf": customer.cpf if customer and customer.cpf else "",
		"customer_cnpj": customer.cnpj if customer and customer.cnpj else "",
		"customer_rg": customer.rg if customer and customer.rg else "",
		"customer_trade_name": customer.trade_name if customer and customer.trade_name else "",
		"customer_nationality": customer.nationality if customer and customer.nationality else "",
		"customer_marital_status": customer.marital_status if customer and customer.marital_status else "",
		"customer_profession": customer.profession if customer and customer.profession else "",
		"customer_legal_representative": customer.legal_representative if customer else "",
		"address_street": addr.street if addr else "",
		"address_number": addr.number if addr else "",
		"address_complement": addr.complement if addr else "",
		"address_district": addr.district if addr else "",
		"address_city": addr.city if addr else "",
		"address_state": addr.state if addr else "",
		"address_cep": addr.cep if addr else "",
		"address_full": customer_address_full,
		"contact_name": contact.contact_name if contact else "",
		"contact_phone": contact.phone if contact else "",
		"contact_email": (contact.email or "").lower() if contact and contact.email else "",
		"telefone": contact.phone if contact else "",
		"email": (contact.email or "").lower() if contact and contact.email else "",
		"project": project.name,
		"project_title": project.title or project.name,
		"titulo_obra": project.title or project.name,
		"project_city": project.city or "",
		"project_status": project.status or "",
		"project_type": project.project_type or "",
		"project_address_street": project.address_street or "",
		"project_address_number": project.address_number or "",
		"project_address_district": project.address_district or "",
		"project_address_cep": project.address_cep or "",
		"project_address_full": project_address_full,
		"project_construction_area": flt(project.construction_area),
		"spec_project_total": spec_total,
		"contract_name": contract_row.name if contract_row else "",
		"contract_value": flt(contract_row.current_value) if contract_row else 0,
		"contract_status": contract_row.status if contract_row else "",
		"today": formatdate(today()),
		"today_iso": getdate(today()).isoformat(),
	}


def _render_and_attach(project_name, template_doc, context):
	try:
		from docxtpl import DocxTemplate
	except ImportError:
		frappe.throw(_("Biblioteca docxtpl não instalada. Contate o administrador."))

	if not template_doc.document_file:
		frappe.throw(_("Template sem arquivo .docx anexado."))

	file_doc = frappe.get_doc("File", {"file_url": template_doc.document_file})
	file_path = file_doc.get_full_path()
	if not os.path.exists(file_path):
		frappe.throw(_("Arquivo do template não encontrado no servidor."))

	tpl = DocxTemplate(file_path)
	tpl.render(context)

	buffer = io.BytesIO()
	tpl.save(buffer)
	buffer.seek(0)

	doc_type = re.sub(r"[^\w\-]+", "_", template_doc.document_type or "doc").strip("_")
	project_slug = re.sub(r"[^\w\-]+", "_", project_name).strip("_")
	date_slug = frappe.utils.now_datetime().strftime("%Y%m%d")
	file_name = f"{doc_type}_{project_slug}_{date_slug}.docx"

	attachment = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": file_name,
			"content": buffer.read(),
			"attached_to_doctype": "Construction Project",
			"attached_to_name": project_name,
			"is_private": 1,
		}
	)
	attachment.save(ignore_permissions=True)  # File anexado — write no Construction Project já validada
	return {"file_url": attachment.file_url, "file_name": file_name}
