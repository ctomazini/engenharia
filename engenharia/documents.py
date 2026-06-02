import io
import json
import os
import re

import frappe
from frappe import _
from frappe.utils import flt, formatdate, getdate, today

from engenharia.titles import get_customer_name


@frappe.whitelist()
def generate_project_documents(project_name: str, template_names):
	frappe.has_permission("Construction Project", "write", throw=True)
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
		except Exception as exc:
			failures.append({"template": template_name, "error": str(exc)})
			frappe.log_error(
				title=f"Erro ao gerar documento {template_name}",
				message=frappe.get_traceback(),
			)

	return {"generated": generated, "failures": failures, "total": len(generated)}


@frappe.whitelist()
def get_available_templates():
	frappe.has_permission("Document Template", "read", throw=True)
	return frappe.get_all(
		"Document Template",
		filters={"enabled": 1},
		fields=["name", "title", "document_type"],
		order_by="title asc",
		limit=100,
	)


def _parse_template_names(template_names):
	if isinstance(template_names, str):
		template_names = json.loads(template_names or "[]")
	if not isinstance(template_names, list):
		frappe.throw(_("Lista de templates inválida."))
	return [name for name in template_names if name]


def _build_context(project_name):
	project = frappe.get_doc("Construction Project", project_name)
	customer = frappe.get_doc("Customer", project.customer) if project.customer else None
	contract = frappe.get_all(
		"Engineering Contract",
		filters={"project": project.name, "status": ["!=", "Cancelado"]},
		fields=["name", "current_value", "status"],
		order_by="modified desc",
		limit=1,
	)
	contract_row = contract[0] if contract else None

	return {
		"project": project.name,
		"project_title": project.title or project.name,
		"project_city": project.city or "",
		"project_status": project.status or "",
		"project_type": project.project_type or "",
		"customer_name": get_customer_name(project.customer),
		"customer_cpf": customer.cpf if customer and customer.cpf else "",
		"customer_cnpj": customer.cnpj if customer and customer.cnpj else "",
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
