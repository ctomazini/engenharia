import io
import json
import os
import re

import frappe
from frappe import _
from frappe.utils import flt, formatdate, fmt_money, getdate, strip_html, today

from engenharia.project_rollup import get_project_items_summary
from engenharia.titles import get_customer_name

PLACEHOLDER_REFERENCE = [
	{
		"grupo": "Escritório",
		"items": [
			{"placeholder": "company_name", "label": "Nome do escritório"},
			{"placeholder": "company_cnpj", "label": "CNPJ do escritório"},
			{"placeholder": "company_crea", "label": "CREA do escritório"},
			{"placeholder": "company_logo", "label": "URL do logotipo (Configurações da Engenharia)"},
			{"placeholder": "bank_name", "label": "Banco"},
			{"placeholder": "bank_agency", "label": "Agência"},
			{"placeholder": "bank_account", "label": "Conta bancária"},
			{"placeholder": "bank_pix", "label": "Chave PIX"},
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
			{"placeholder": "customer_legal_representative_cpf", "label": "CPF do representante legal"},
			{"placeholder": "customer_legal_representative_role", "label": "Cargo do representante legal"},
			{"placeholder": "customer_legal_representative_nationality", "label": "Nacionalidade do representante"},
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
			{"placeholder": "contact_phone", "label": "Telefone fixo", "alias": "telefone"},
			{"placeholder": "contact_mobile", "label": "Celular"},
			{"placeholder": "contact_email", "label": "E-mail", "alias": "email"},
		],
	},
	{
		"grupo": "Obra",
		"items": [
			{"placeholder": "project", "label": "Código da obra"},
			{"placeholder": "project_title", "label": "Título da obra", "alias": "titulo_obra"},
			{"placeholder": "project_status", "label": "Status da obra"},
			{"placeholder": "project_type", "label": "Tipo de obra"},
			{"placeholder": "project_start_date", "label": "Data de início"},
			{"placeholder": "project_expected_delivery", "label": "Previsão de entrega"},
			{"placeholder": "project_address_street", "label": "Logradouro da obra"},
			{"placeholder": "project_address_number", "label": "Número da obra"},
			{"placeholder": "project_address_district", "label": "Bairro da obra"},
			{"placeholder": "project_city", "label": "Cidade da obra"},
			{"placeholder": "project_address_uf", "label": "UF da obra"},
			{"placeholder": "project_address_cep", "label": "CEP da obra"},
			{"placeholder": "project_address_full", "label": "Endereço completo da obra"},
			{"placeholder": "project_construction_area", "label": "Área construída (m²)"},
			{"placeholder": "project_current_contract_value", "label": "Valor atual do contrato (R$)"},
			{"placeholder": "project_current_contract_value_fmt", "label": "Valor atual do contrato (formatado)"},
			{"placeholder": "project_physical_progress", "label": "Avanço físico global (%)"},
			{"placeholder": "project_responsible_engineer", "label": "Responsável técnico"},
			{"placeholder": "project_crea_number", "label": "CREA do responsável"},
			{"placeholder": "project_art_number", "label": "Nº ART principal"},
			{"placeholder": "project_property_registration", "label": "Matrícula do imóvel"},
			{"placeholder": "project_gps_coordinates", "label": "Coordenadas GPS"},
			{"placeholder": "project_budget_revision", "label": "Revisão vigente do orçamento"},
			{"placeholder": "project_default_bdi_percent", "label": "BDI padrão da obra (%)"},
			{"placeholder": "spec_project_total", "label": "Total do orçamento (R$)"},
			{"placeholder": "spec_project_total_fmt", "label": "Total do orçamento (formatado)"},
			{"placeholder": "project_observations", "label": "Observações da obra"},
		],
	},
	{
		"grupo": "Orçamento (obra)",
		"items": [
			{"placeholder": "project_item_count", "label": "Quantidade de itens do orçamento (revisão vigente)"},
			{
				"placeholder": "project_items",
				"label": "Lista de itens do orçamento (use {% for item in project_items %})",
			},
		],
	},
	{
		"grupo": "Item do orçamento (loop)",
		"condicional": True,
		"items": [
			{"placeholder": "name", "label": "Código do item", "loop_only": True, "loop_var": "item"},
			{"placeholder": "title", "label": "Título do item", "loop_only": True, "loop_var": "item"},
			{"placeholder": "technical_item", "label": "Item técnico (catálogo)", "loop_only": True, "loop_var": "item"},
			{"placeholder": "instance_label", "label": "Identificação / instância", "loop_only": True, "loop_var": "item"},
			{"placeholder": "quantity", "label": "Quantidade", "loop_only": True, "loop_var": "item"},
			{"placeholder": "unit", "label": "Unidade", "loop_only": True, "loop_var": "item"},
			{"placeholder": "unit_price", "label": "Preço unitário (R$)", "loop_only": True, "loop_var": "item"},
			{"placeholder": "unit_price_fmt", "label": "Preço unitário (formatado)", "loop_only": True, "loop_var": "item"},
			{"placeholder": "total_value", "label": "Valor total (R$)", "loop_only": True, "loop_var": "item"},
			{"placeholder": "total_value_fmt", "label": "Valor total (formatado)", "loop_only": True, "loop_var": "item"},
			{"placeholder": "params_summary", "label": "Resumo dos parâmetros", "loop_only": True, "loop_var": "item"},
			{"placeholder": "outputs_summary", "label": "Resumo dos resultados calculados", "loop_only": True, "loop_var": "item"},
		],
	},
	{
		"grupo": "Subcontratos (obra)",
		"items": [
			{"placeholder": "subcontract_count", "label": "Quantidade de subcontratos"},
			{"placeholder": "subcontract_total_value", "label": "Valor total acordado (R$)"},
			{"placeholder": "subcontract_total_value_fmt", "label": "Valor total acordado (formatado)"},
			{"placeholder": "subcontract_total_paid", "label": "Total já pago a prestadores (R$)"},
			{"placeholder": "subcontract_total_paid_fmt", "label": "Total já pago (formatado)"},
			{"placeholder": "subcontract_outstanding", "label": "Saldo a pagar a prestadores (R$)"},
			{"placeholder": "subcontract_outstanding_fmt", "label": "Saldo a pagar (formatado)"},
			{
				"placeholder": "subcontracts",
				"label": "Lista de subcontratos (use {% for s in subcontracts %})",
			},
		],
	},
	{
		"grupo": "Subcontrato (item do loop)",
		"condicional": True,
		"items": [
			{"placeholder": "name", "label": "Código do subcontrato", "loop_only": True, "loop_var": "s"},
			{"placeholder": "title", "label": "Título do subcontrato", "loop_only": True, "loop_var": "s"},
			{"placeholder": "supplier", "label": "Código do prestador (Link)", "loop_only": True, "loop_var": "s"},
			{"placeholder": "supplier_name", "label": "Nome do prestador", "loop_only": True, "loop_var": "s"},
			{"placeholder": "supplier_cnpj", "label": "CNPJ do prestador", "loop_only": True, "loop_var": "s"},
			{"placeholder": "funded_by", "label": "Quem arca (Escritório / Cliente)", "loop_only": True, "loop_var": "s"},
			{"placeholder": "description", "label": "Descrição do serviço", "loop_only": True, "loop_var": "s"},
			{"placeholder": "total_value", "label": "Valor acordado (R$)", "loop_only": True, "loop_var": "s"},
			{"placeholder": "total_value_fmt", "label": "Valor acordado (formatado)", "loop_only": True, "loop_var": "s"},
			{"placeholder": "total_paid", "label": "Total pago (R$)", "loop_only": True, "loop_var": "s"},
			{"placeholder": "total_paid_fmt", "label": "Total pago (formatado)", "loop_only": True, "loop_var": "s"},
			{"placeholder": "outstanding", "label": "Saldo a pagar (R$)", "loop_only": True, "loop_var": "s"},
			{"placeholder": "outstanding_fmt", "label": "Saldo a pagar (formatado)", "loop_only": True, "loop_var": "s"},
			{"placeholder": "status", "label": "Status", "loop_only": True, "loop_var": "s"},
			{"placeholder": "cost_category", "label": "Categoria de custo", "loop_only": True, "loop_var": "s"},
			{"placeholder": "amendment_remarks", "label": "Observações de aditivo", "loop_only": True, "loop_var": "s"},
			{
				"placeholder": "payments",
				"label": "Parcelas pagas (use {% for p in s.payments %})",
				"loop_only": True,
				"loop_var": "s",
			},
		],
	},
	{
		"grupo": "Pagamento de subcontrato (item do loop)",
		"condicional": True,
		"items": [
			{"placeholder": "payment_date", "label": "Data do pagamento", "loop_only": True, "loop_var": "p"},
			{"placeholder": "payment_date_fmt", "label": "Data do pagamento (formatada)", "loop_only": True, "loop_var": "p"},
			{"placeholder": "amount", "label": "Valor pago (R$)", "loop_only": True, "loop_var": "p"},
			{"placeholder": "amount_fmt", "label": "Valor pago (formatado)", "loop_only": True, "loop_var": "p"},
			{"placeholder": "payment_method", "label": "Forma de pagamento", "loop_only": True, "loop_var": "p"},
			{"placeholder": "reference", "label": "Referência / comprovante", "loop_only": True, "loop_var": "p"},
			{"placeholder": "remarks", "label": "Observações", "loop_only": True, "loop_var": "p"},
		],
	},
	{
		"grupo": "Contrato",
		"condicional": True,
		"items": [
			{"placeholder": "contract_name", "label": "Código do contrato"},
			{"placeholder": "contract_title", "label": "Título do contrato"},
			{"placeholder": "contract_status", "label": "Status do contrato"},
			{"placeholder": "contract_base_value", "label": "Valor base (R$)"},
			{"placeholder": "contract_base_value_fmt", "label": "Valor base (formatado)"},
			{"placeholder": "contract_value", "label": "Valor atual (R$)"},
			{"placeholder": "contract_value_fmt", "label": "Valor atual (formatado)"},
			{"placeholder": "contract_adjustment_index", "label": "Índice de reajuste"},
			{"placeholder": "contract_technical_retention_pct", "label": "Retenção técnica (%)"},
			{"placeholder": "contract_late_fee_pct", "label": "Multa mora (%)"},
			{"placeholder": "contract_daily_interest_pct", "label": "Juros diários (%)"},
			{"placeholder": "contract_installment_count", "label": "Número de parcelas"},
			{"placeholder": "contract_first_installment_date", "label": "Data da 1ª parcela"},
			{"placeholder": "contract_installment_value", "label": "Valor da parcela (R$)"},
			{"placeholder": "contract_installment_value_fmt", "label": "Valor da parcela (formatado)"},
			{"placeholder": "contract_observations", "label": "Observações do contrato"},
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
def generate_project_documents(project_name: str, template_names: str | list) -> dict:
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
					"title": template_doc.template_name,
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
		fields=["name", "template_name", "document_type", "description"],
		order_by="template_name asc",
		limit=100,
	)


@frappe.whitelist()
def get_available_kits() -> list[dict]:
	frappe.has_permission("Document Kit", "read", throw=True)

	kits = frappe.get_all(
		"Document Kit",
		fields=["name", "kit_name", "description"],
		filters={"enabled": 1},
		order_by="kit_name asc",
		limit=100,
	)
	if not kits:
		return kits

	kit_names = [row.name for row in kits]
	item_rows = frappe.get_all(
		"Document Kit Item",
		filters={"parent": ["in", kit_names]},
		fields=["parent", "document_template", "sort_order"],
		order_by="parent asc, sort_order asc, idx asc",
		limit=500,
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


def get_document_placeholder_keys() -> set[str]:
	keys = set()
	for block in PLACEHOLDER_REFERENCE:
		for item in block.get("items") or []:
			if item.get("loop_only"):
				continue
			keys.add(item["placeholder"])
			if item.get("alias"):
				keys.add(item["alias"])
	return keys


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


def _fmt_date(value) -> str:
	if not value:
		return ""
	return formatdate(getdate(value))


def _fmt_currency(value) -> str:
	return fmt_money(flt(value))


def _get_settings_context(settings) -> dict:
	return {
		"company_name": settings.company_name or "",
		"company_cnpj": settings.company_cnpj or "",
		"company_crea": settings.company_crea or "",
		"company_logo": settings.company_logo or "",
		"bank_name": settings.bank_name or "",
		"bank_agency": settings.bank_agency or "",
		"bank_account": settings.bank_account or "",
		"bank_pix": settings.bank_pix or "",
	}


def _get_customer_context(customer, addr, contact) -> dict:
	customer_name = get_customer_name(customer.name) if customer else ""
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
		"customer_name": customer_name,
		"nome": customer_name,
		"customer_person_type": customer.person_type if customer else "",
		"customer_cpf": customer.cpf if customer and customer.cpf else "",
		"customer_cnpj": customer.cnpj if customer and customer.cnpj else "",
		"customer_rg": customer.rg if customer and customer.rg else "",
		"cpf": customer.cpf if customer and customer.cpf else "",
		"cnpj": customer.cnpj if customer and customer.cnpj else "",
		"rg": customer.rg if customer and customer.rg else "",
		"customer_trade_name": customer.trade_name if customer and customer.trade_name else "",
		"customer_nationality": customer.nationality if customer and customer.nationality else "",
		"customer_marital_status": customer.marital_status if customer and customer.marital_status else "",
		"customer_profession": customer.profession if customer and customer.profession else "",
		"customer_legal_representative": (customer.legal_representative or "") if customer else "",
		"customer_legal_representative_cpf": (customer.legal_representative_cpf or "") if customer else "",
		"customer_legal_representative_role": (customer.legal_representative_role or "") if customer else "",
		"customer_legal_representative_nationality": (customer.legal_representative_nationality or "") if customer else "",
		"address_street": addr.street if addr else "",
		"address_number": addr.number if addr else "",
		"address_complement": addr.complement if addr else "",
		"address_district": addr.district if addr else "",
		"address_city": addr.city if addr else "",
		"address_state": addr.state if addr else "",
		"address_cep": addr.cep if addr else "",
		"endereco": addr.street if addr else "",
		"numero": addr.number if addr else "",
		"bairro": addr.district if addr else "",
		"cidade": addr.city if addr else "",
		"estado": addr.state if addr else "",
		"cep": addr.cep if addr else "",
		"address_full": customer_address_full,
		"contact_name": contact.contact_name if contact else "",
		"contact_phone": contact.phone if contact else "",
		"contact_mobile": contact.mobile if contact else "",
		"contact_email": (contact.email or "").lower() if contact and contact.email else "",
		"telefone": contact.phone if contact else "",
		"email": (contact.email or "").lower() if contact and contact.email else "",
	}


def _get_project_context(project) -> dict:
	spec_total = flt(project.spec_project_total)
	current_contract_value = flt(project.current_contract_value)
	project_address_full = _format_full_address(
		project.address_street,
		project.address_number,
		None,
		project.address_district,
		project.city,
		project.address_uf,
		project.address_cep,
	)
	return {
		"project": project.name,
		"project_title": project.title or project.name,
		"titulo_obra": project.title or project.name,
		"project_status": project.status or "",
		"project_type": project.project_type or "",
		"project_start_date": _fmt_date(project.start_date),
		"project_expected_delivery": _fmt_date(project.expected_delivery),
		"project_address_street": project.address_street or "",
		"project_address_number": project.address_number or "",
		"project_address_district": project.address_district or "",
		"project_city": project.city or "",
		"project_address_uf": project.address_uf or "",
		"project_address_cep": project.address_cep or "",
		"project_address_full": project_address_full,
		"project_construction_area": flt(project.construction_area),
		"project_current_contract_value": current_contract_value,
		"project_current_contract_value_fmt": _fmt_currency(current_contract_value),
		"project_physical_progress": flt(project.physical_progress),
		"project_responsible_engineer": project.responsible_engineer or "",
		"project_crea_number": project.crea_number or "",
		"project_art_number": project.art_number or "",
		"project_property_registration": project.property_registration or "",
		"project_gps_coordinates": project.gps_coordinates or "",
		"project_budget_revision": project.budget_revision or 1,
		"project_default_bdi_percent": flt(project.default_bdi_percent),
		"spec_project_total": spec_total,
		"spec_project_total_fmt": _fmt_currency(spec_total),
		"project_observations": strip_html(project.observations or ""),
	}


def _get_subcontract_payment_row(payment) -> dict:
	amount = flt(payment.amount)
	return {
		"payment_date": payment.payment_date or "",
		"payment_date_fmt": _fmt_date(payment.payment_date),
		"amount": amount,
		"amount_fmt": _fmt_currency(amount),
		"payment_method": payment.payment_method or "",
		"reference": payment.reference or "",
		"remarks": payment.remarks or "",
	}


def _get_subcontracts_context(project_name: str) -> dict:
	rows = frappe.get_all(
		"Subcontract",
		filters={"project": project_name, "status": ["!=", "Cancelled"]},
		fields=[
			"name",
			"title",
			"supplier",
			"description",
			"total_value",
			"total_paid",
			"outstanding",
			"status",
			"cost_category",
			"amendment_remarks",
			"funded_by",
		],
		order_by="creation asc",
		limit=100,
	)
	supplier_names = {}
	supplier_cnpjs = {}
	if rows:
		suppliers = frappe.get_all(
			"Supplier",
			filters={"name": ["in", [row.supplier for row in rows if row.supplier]]},
			fields=["name", "supplier_name", "cnpj"],
			limit=100,
		)
		supplier_names = {row.name: row.supplier_name for row in suppliers}
		supplier_cnpjs = {row.name: row.cnpj or "" for row in suppliers}

	subcontracts = []
	total_value = 0.0
	total_paid = 0.0
	outstanding = 0.0

	for row in rows:
		payment_rows = frappe.get_all(
			"Subcontract Payment",
			filters={"parent": row.name},
			fields=["payment_date", "amount", "payment_method", "reference", "remarks"],
			order_by="payment_date asc, idx asc",
			limit=50,
		)
		row_total = flt(row.total_value)
		row_paid = flt(row.total_paid)
		row_outstanding = flt(row.outstanding)
		total_value += row_total
		total_paid += row_paid
		outstanding += row_outstanding

		subcontracts.append(
			{
				"name": row.name,
				"title": row.title or row.name,
				"supplier": row.supplier or "",
				"supplier_name": supplier_names.get(row.supplier, row.supplier or ""),
				"supplier_cnpj": supplier_cnpjs.get(row.supplier, ""),
				"funded_by": row.funded_by or "",
				"description": row.description or "",
				"total_value": row_total,
				"total_value_fmt": _fmt_currency(row_total),
				"total_paid": row_paid,
				"total_paid_fmt": _fmt_currency(row_paid),
				"outstanding": row_outstanding,
				"outstanding_fmt": _fmt_currency(row_outstanding),
				"status": row.status or "",
				"cost_category": row.cost_category or "",
				"amendment_remarks": row.amendment_remarks or "",
				"payments": [_get_subcontract_payment_row(payment) for payment in payment_rows],
			}
		)

	return {
		"subcontract_count": len(subcontracts),
		"subcontract_total_value": total_value,
		"subcontract_total_value_fmt": _fmt_currency(total_value),
		"subcontract_total_paid": total_paid,
		"subcontract_total_paid_fmt": _fmt_currency(total_paid),
		"subcontract_outstanding": outstanding,
		"subcontract_outstanding_fmt": _fmt_currency(outstanding),
		"subcontracts": subcontracts,
	}


def _get_project_items_context(project_name: str) -> dict:
	summary = get_project_items_summary(project_name)
	items = []
	for row in summary.get("items") or []:
		total = flt(row.get("total_value"))
		unit_price = flt(row.get("unit_price"))
		items.append(
			{
				"name": row.get("name") or "",
				"title": row.get("title") or "",
				"technical_item": row.get("technical_item") or "",
				"instance_label": row.get("instance_label") or "",
				"quantity": flt(row.get("quantity")),
				"unit": row.get("unit") or "",
				"unit_price": unit_price,
				"unit_price_fmt": _fmt_currency(unit_price),
				"total_value": total,
				"total_value_fmt": _fmt_currency(total),
				"params_summary": row.get("params_summary") or "",
				"outputs_summary": row.get("outputs_summary") or "",
			}
		)
	return {
		"project_item_count": len(items),
		"project_items": items,
	}


def _get_contract_context(contract) -> dict:
	if not contract:
		return {
			"contract_name": "",
			"contract_title": "",
			"contract_status": "",
			"contract_base_value": 0,
			"contract_base_value_fmt": _fmt_currency(0),
			"contract_value": 0,
			"contract_value_fmt": _fmt_currency(0),
			"contract_adjustment_index": "",
			"contract_technical_retention_pct": 0,
			"contract_late_fee_pct": 0,
			"contract_daily_interest_pct": 0,
			"contract_installment_count": 0,
			"contract_first_installment_date": "",
			"contract_installment_value": 0,
			"contract_installment_value_fmt": _fmt_currency(0),
			"contract_observations": "",
		}

	base_value = flt(contract.base_value)
	current_value = flt(contract.current_value)
	installment_value = flt(contract.installment_value)
	return {
		"contract_name": contract.name,
		"contract_title": contract.title or contract.name,
		"contract_status": contract.status or "",
		"contract_base_value": base_value,
		"contract_base_value_fmt": _fmt_currency(base_value),
		"contract_value": current_value,
		"contract_value_fmt": _fmt_currency(current_value),
		"contract_adjustment_index": contract.adjustment_index or "",
		"contract_technical_retention_pct": flt(contract.technical_retention_pct),
		"contract_late_fee_pct": flt(contract.late_fee_pct),
		"contract_daily_interest_pct": flt(contract.daily_interest_pct),
		"contract_installment_count": contract.installment_count or 0,
		"contract_first_installment_date": _fmt_date(contract.first_installment_date),
		"contract_installment_value": installment_value,
		"contract_installment_value_fmt": _fmt_currency(installment_value),
		"contract_observations": strip_html(contract.observations or ""),
	}


def _build_context(project_name: str) -> dict:
	project = frappe.get_doc("Construction Project", project_name)
	customer = frappe.get_doc("Customer", project.customer) if project.customer else None
	addr = _primary_customer_address(customer)
	contact = _primary_customer_contact(customer)

	contract_name = frappe.db.get_value(
		"Engineering Contract",
		{"project": project.name, "status": ["!=", "Cancelado"]},
		"name",
		order_by="modified desc",
	)
	contract = frappe.get_doc("Engineering Contract", contract_name) if contract_name else None
	settings = frappe.get_single("Engineering Settings")

	context = {}
	context.update(_get_settings_context(settings))
	context.update(_get_customer_context(customer, addr, contact))
	context.update(_get_project_context(project))
	context.update(_get_project_items_context(project.name))
	context.update(_get_contract_context(contract))
	context.update(_get_subcontracts_context(project.name))
	context.update(
		{
			"today": formatdate(today()),
			"today_iso": getdate(today()).isoformat(),
		}
	)
	return context


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
