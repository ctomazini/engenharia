import base64
import calendar
from collections import OrderedDict

import frappe
from frappe import _
from frappe.utils import flt, formatdate, getdate, today

from engenharia.documents import (
	_document_format_helpers,
	_fmt_currency,
	_format_full_address,
	_get_settings_context,
	_render_docx_template,
)
from engenharia.validators import formatar_cep, formatar_cnpj, formatar_cpf

_MONTH_NAMES = (
	"",
	"janeiro",
	"fevereiro",
	"março",
	"abril",
	"maio",
	"junho",
	"julho",
	"agosto",
	"setembro",
	"outubro",
	"novembro",
	"dezembro",
)


@frappe.whitelist()
def get_monthly_receivables_report(month: int, year: int, mode: str, template_name: str) -> dict:
	"""Gera relatório mensal de recebimentos (.docx) para o contador.

	Args:
		month: mês de referência (1-12).
		year: ano de referência (4 dígitos).
		mode: "previsao" (vencimentos do mês) ou "realizado" (recebidos no mês).
		template_name: nome do Document Template a usar.

	Returns:
		dict com file_name, file_content (base64), count e total.
	"""
	frappe.has_permission("Payment", "read", throw=True)
	frappe.has_permission("Document Template", "read", throw=True)

	month = int(month)
	year = int(year)

	if mode not in ("previsao", "realizado"):
		frappe.throw(_("O modo deve ser 'previsao' ou 'realizado'."))
	if not 1 <= month <= 12:
		frappe.throw(_("O mês deve estar entre 1 e 12."))

	template_doc = frappe.get_doc("Document Template", template_name)
	if not template_doc.enabled:
		frappe.throw(_("Modelo {0} está desabilitado.").format(template_name))
	if not template_doc.document_file:
		frappe.throw(_("Modelo {0} não possui arquivo .docx anexado.").format(template_name))

	context = _build_receivables_context(month, year, mode)

	mode_label = _("Previsao") if mode == "previsao" else _("Realizado")
	file_name = f"Recebimentos_{mode_label}_{year}-{month:02d}.docx"

	content = _render_docx_template(template_doc, context)

	return {
		"file_name": file_name,
		"file_content": base64.b64encode(content).decode("ascii"),
		"count": context["count"],
		"total": context["total_fmt"],
	}


def _build_receivables_context(month: int, year: int, mode: str) -> dict:
	"""Monta o contexto Jinja do relatório mensal de recebimentos."""
	first_day = getdate(f"{year}-{month:02d}-01")
	last_day = getdate(f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}")

	settings = frappe.get_single("Engineering Settings")
	base_context = {
		**_get_settings_context(settings),
		**_report_header_context(month, year, mode),
		**_document_format_helpers(),
	}

	filters = {"origin_type": "Parcela do Contrato"}
	if mode == "previsao":
		filters["due_date"] = ["between", [str(first_day), str(last_day)]]
		filters["status"] = ["not in", ["Cancelado", "Renegociado"]]
	else:
		filters["received_date"] = ["between", [str(first_day), str(last_day)]]
		filters["status"] = "Recebido"

	payments = frappe.get_all(
		"Payment",
		filters=filters,
		fields=[
			"name",
			"customer",
			"due_date",
			"description",
			"project",
			"contract",
			"installment_number",
			"amount",
			"received_amount",
			"received_date",
			"status",
			"nf_number",
		],
		order_by="customer asc, due_date asc",
		limit_page_length=10000,
	)

	if not payments:
		return {
			**base_context,
			"customers": [],
			"total": 0,
			"total_fmt": _fmt_currency(0),
			"count": 0,
		}

	customer_names = list({p.customer for p in payments if p.customer})
	customers_data = {
		c.name: c
		for c in frappe.get_all(
			"Customer",
			filters={"name": ["in", customer_names]},
			fields=[
				"name",
				"customer_name",
				"person_type",
				"cpf",
				"cnpj",
				"rg",
				"legal_representative",
			],
			limit_page_length=10000,
		)
	}
	addresses_data = _get_primary_addresses_batch(customer_names)

	fmt = _document_format_helpers()

	grouped: "OrderedDict[str, list]" = OrderedDict()
	for p in payments:
		grouped.setdefault(p.customer, []).append(p)

	customers_list = []
	grand_total = 0.0

	for customer_id, parcelas in grouped.items():
		cdata = customers_data.get(customer_id, frappe._dict())

		installments = []
		subtotal = 0.0
		for p in parcelas:
			amount_val = flt(p.amount)
			received_val = flt(p.received_amount)
			# No modo realizado, parcelas marcadas como recebidas sem o valor
			# recebido preenchido caem para o valor da parcela (convenção do financeiro).
			if mode == "previsao":
				valor = amount_val
			else:
				valor = received_val or amount_val
			subtotal += valor
			installments.append(
				{
					"due_date_fmt": formatdate(getdate(p.due_date)) if p.due_date else "",
					"description": p.description or "",
					"project": p.project or "",
					"contract": p.contract or "",
					"installment_number": p.installment_number or "",
					"amount": flt(p.amount),
					"amount_fmt": fmt["real"](flt(p.amount)),
					"received_amount": flt(p.received_amount),
					"received_amount_fmt": fmt["real"](flt(p.received_amount)),
					"received_date_fmt": formatdate(getdate(p.received_date)) if p.received_date else "",
					"status": p.status or "",
					"nf_number": p.nf_number or "",
					"valor": valor,
					"valor_fmt": fmt["real"](valor),
				}
			)

		grand_total += subtotal

		person_type = cdata.get("person_type") or ""
		cpf = formatar_cpf(cdata.cpf) if cdata.get("cpf") else ""
		cnpj = formatar_cnpj(cdata.cnpj) if cdata.get("cnpj") else ""
		if person_type == "Pessoa Jurídica" and cnpj:
			cpf_cnpj, cpf_cnpj_label = cnpj, "CNPJ"
		elif cpf:
			cpf_cnpj, cpf_cnpj_label = cpf, "CPF"
		else:
			cpf_cnpj, cpf_cnpj_label = cnpj, ("CNPJ" if cnpj else "")

		customers_list.append(
			{
				"customer": customer_id,
				"customer_name": cdata.get("customer_name") or customer_id,
				"person_type": person_type,
				"cpf_cnpj_label": cpf_cnpj_label,
				"cpf_cnpj": cpf_cnpj,
				"cpf": cpf,
				"cnpj": cnpj,
				"rg": cdata.get("rg") or "",
				"legal_representative": cdata.get("legal_representative") or "",
				"address_full": addresses_data.get(customer_id, ""),
				"installments": installments,
				"subtotal": subtotal,
				"subtotal_fmt": fmt["real"](subtotal),
				"count": len(installments),
			}
		)

	return {
		**base_context,
		"customers": customers_list,
		"total": grand_total,
		"total_fmt": fmt["real"](grand_total),
		"count": sum(c["count"] for c in customers_list),
	}


def _report_header_context(month: int, year: int, mode: str) -> dict:
	"""Cabeçalho do relatório de recebimentos."""
	mode_label = _("Previsão") if mode == "previsao" else _("Realizado")
	return {
		"report_title": _("Relatório de Recebimentos"),
		"mode_label": mode_label,
		"mode": mode,
		"month_label": f"{_MONTH_NAMES[month]}/{year}",
		"reference_month": f"{month:02d}/{year}",
		"today": formatdate(getdate(today())),
	}


def _get_primary_addresses_batch(customer_names: list[str]) -> dict[str, str]:
	"""Retorna {customer: endereço formatado} usando a child Customer Address em lote."""
	if not customer_names:
		return {}

	rows = frappe.get_all(
		"Customer Address",
		filters={"parenttype": "Customer", "parent": ["in", customer_names]},
		fields=[
			"parent",
			"street",
			"number",
			"complement",
			"district",
			"city",
			"state",
			"cep",
			"is_primary",
			"idx",
		],
		order_by="parent asc, is_primary desc, idx asc",
		limit_page_length=10000,
	)

	result: dict[str, str] = {}
	for row in rows:
		if row.parent in result:
			continue
		result[row.parent] = _format_full_address(
			row.street,
			row.number,
			row.complement,
			row.district,
			row.city,
			row.state,
			formatar_cep(row.cep) if row.cep else "",
		)
	return result
