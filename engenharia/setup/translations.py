import frappe

DOCTYPE_LABELS = {
	"Construction Project": "Obra",
	"Engineering Contract": "Contrato de Obra",
	"Work Cost": "Custo da Obra",
	"Reimbursable Expense": "Despesa Reembolsável",
	"Communication Log": "Comunicação",
	"Time Log": "Registro de Horas",
	"Document Template": "Template de Documento",
	"Permit": "Protocolo",
	"Deadline": "Prazo",
	"Permit Type": "Tipo de Protocolo",
	"Payment": "Pagamento",
	"Customer": "Cliente",
	"Task": "Tarefa",
	"Project Item": "Item do Projeto",
	"Project Stage": "Etapa da Obra",
	"Technical Item": "Item Técnico",
	"Supplier": "Fornecedor",
	"Public Agency": "Órgão Público",
	"Cost Category": "Categoria de Custo",
	"Stage Type": "Tipo de Etapa",
	"Document Kit": "Kit de Documentos",
	"Engineering Settings": "Configurações",
	"Project Item Parameter": "Parâmetro do Item",
	"Project Item Output": "Resultado do Item",
	"Technical Item Field": "Campo Técnico",
	"Technical Item Output": "Resultado Técnico",
	"Document Kit Item": "Item do Kit",
	"Customer Contact": "Contato do Cliente",
	"Customer Address": "Endereço do Cliente",
	"Engineering Contract Installment": "Parcela do Contrato",
	"Engineering Contract Amendment": "Aditivo Contratual",
	"Construction Measurement": "Boletim de Medição",
	"Construction Measurement Item": "Item do Boletim",
	"Commission": "Comissão",
	"Commission Payment": "Pagamento de Comissão",
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
