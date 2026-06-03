import frappe

DOCTYPE_LABELS = {
	"Construction Project": "Obra",
	"Engineering Contract": "Contrato de Obra",
	"Work Cost": "Custo da Obra",
	"Reimbursable Expense": "Despesa Reembolsável",
	"Communication Log": "Comunicação",
	"Time Log": "Registro de Horas",
	"Document Template": "Template de Documento",
	"Document Kit": "Kit de Documentos",
}


def ensure_doctype_translations():
	"""Traduz nomes de DocType exibidos na UI (nome interno permanece inalterado)."""
	languages = ["pt", "pt-BR"]
	for source, translated in DOCTYPE_LABELS.items():
		for lang in languages:
			if not frappe.db.exists("Language", lang):
				continue
			if frappe.db.exists(
				"Translation",
				{"source_text": source, "language": lang, "translated_text": translated},
			):
				continue
			if frappe.db.exists("Translation", {"source_text": source, "language": lang}):
				frappe.db.set_value(
					"Translation",
					{"source_text": source, "language": lang},
					"translated_text",
					translated,
					update_modified=True,
				)
				continue
			frappe.get_doc(
				{
					"doctype": "Translation",
					"language": lang,
					"source_text": source,
					"translated_text": translated,
					"contributed": 0,
				}
			).insert(ignore_permissions=True)  # setup: seed de traduções
	frappe.clear_cache()
	frappe.db.commit()  # setup: seed de traduções no migrate
