import base64
import io
import json
import os
import re

import frappe
from frappe import _
from frappe.utils import flt, formatdate, fmt_money, getdate, strip_html, today

from engenharia.project_document_naming import compose_project_document_filename
from engenharia.project_rollup import get_project_items_summary
from engenharia.titles import get_customer_name
from engenharia.validators import formatar_cep, formatar_cnpj, formatar_cpf, formatar_telefone
from num2words import num2words as _num2words

TEMPLATE_CATEGORY_MAP = {
	"memorial": "Memorial",
	"art": "ART",
	"contrato": "Contrato",
	"autorizacao": "Declaração",
	"declaracao": "Declaração",
	"requerimento": "Protocolo",
	"formulario": "Protocolo",
	"laudo": "Laudo",
	"orcamento": "Orçamento",
	"planta": "Planta",
	"alvara": "Alvará",
	"foto": "Foto",
}

PLACEHOLDER_REFERENCE = [
	{
		"grupo": "Escritório",
		"items": [
			{"placeholder": "company_name", "label": "Nome do escritório"},
			{"placeholder": "company_cnpj", "label": "CNPJ do escritório"},
			{"placeholder": "company_crea", "label": "CREA do escritório"},
			{"placeholder": "company_logo", "label": "URL do logotipo (Configurações do Escritório)"},
			{"placeholder": "company_address_full", "label": "Endereço do escritório"},
			{"placeholder": "bank_name", "label": "Banco"},
			{"placeholder": "bank_agency", "label": "Agência"},
			{"placeholder": "bank_account", "label": "Conta bancária"},
			{"placeholder": "bank_pix", "label": "Chave PIX"},
		],
	},
	{
		"grupo": "Engenheiro responsável",
		"items": [
			{"placeholder": "engineer_full_name", "label": "Nome completo do engenheiro responsável"},
			{"placeholder": "engineer_cpf", "label": "CPF do engenheiro"},
			{"placeholder": "engineer_phone", "label": "Telefone do engenheiro"},
			{"placeholder": "engineer_email", "label": "E-mail do engenheiro"},
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
			{"placeholder": "customer_rg_issuer", "label": "Órgão emissor do RG"},
			{"placeholder": "customer_birth_date", "label": "Data de nascimento"},
			{"placeholder": "customer_birth_date_fmt", "label": "Data de nascimento (formatada)"},
			{"placeholder": "customer_trade_name", "label": "Nome fantasia"},
			{"placeholder": "customer_nationality", "label": "Nacionalidade"},
			{"placeholder": "customer_marital_status", "label": "Estado civil"},
			{"placeholder": "customer_profession", "label": "Profissão"},
			{"placeholder": "customer_legal_representative", "label": "Representante legal"},
			{"placeholder": "customer_legal_representative_cpf", "label": "CPF do representante legal"},
			{"placeholder": "customer_legal_representative_role", "label": "Cargo do representante legal"},
			{"placeholder": "customer_legal_representative_nationality", "label": "Nacionalidade do representante"},
			{"placeholder": "customer_observations", "label": "Observações do cliente"},
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
			{"placeholder": "project_location_code", "label": "Código de localização municipal"},
			{"placeholder": "project_dic", "label": "DIC (cadastro municipal do lote)"},
			{"placeholder": "project_construction_area", "label": "Área construída (m²) — valor numérico"},
			{"placeholder": "project_construction_area_fmt", "label": "Área construída (m²) — formatado"},
			{"placeholder": "project_current_contract_value", "label": "Soma dos contratos da obra (R$) — total, não um contrato"},
			{"placeholder": "project_current_contract_value_fmt", "label": "Soma dos contratos da obra (formatado)"},
			{"placeholder": "project_physical_progress", "label": "Avanço físico global (%) — valor numérico"},
			{"placeholder": "project_physical_progress_fmt", "label": "Avanço físico global (%) — formatado"},
			{"placeholder": "project_responsible_engineer", "label": "Responsável técnico"},
			{"placeholder": "project_crea_number", "label": "CREA do responsável"},
			{"placeholder": "project_art_number", "label": "Nº ART principal"},
			{"placeholder": "project_art_execution_number", "label": "Nº ART de execução (distinta da ART de projeto)"},
			{"placeholder": "project_building_type", "label": "Tipo de edificação (código Link)"},
			{"placeholder": "project_building_type_label", "label": "Tipo de edificação (nome legível)"},
			{"placeholder": "project_main_material", "label": "Material principal da edificação"},
			{"placeholder": "project_unit_count", "label": "Nº de economias"},
			{"placeholder": "project_estimated_population", "label": "População estimada"},
			{"placeholder": "project_occupancy_permit", "label": "Nº do habite-se existente"},
			{"placeholder": "project_structural_engineer", "label": "Responsável técnico estrutura"},
			{"placeholder": "project_structural_company", "label": "Empresa responsável pela estrutura"},
			{"placeholder": "project_structural_engineer_crea", "label": "CREA do responsável estrutural"},
			{"placeholder": "project_structural_art_number", "label": "Nº ART estrutural"},
			{"placeholder": "project_property_registration", "label": "Matrícula do imóvel"},
			{"placeholder": "project_gps_coordinates", "label": "Coordenadas GPS"},
			{"placeholder": "project_budget_revision", "label": "Revisão vigente do orçamento"},
			{"placeholder": "project_default_bdi_percent", "label": "BDI padrão da obra (%) — valor numérico"},
			{"placeholder": "project_default_bdi_percent_fmt", "label": "BDI padrão da obra (%) — formatado"},
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
		"condicional_motivo": "Campos dentro de {% for item in project_items %}",
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
		"condicional_motivo": "Campos dentro de {% for s in subcontracts %}",
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
			{"placeholder": "cost_category", "label": "Categoria de custo (código Link)", "loop_only": True, "loop_var": "s"},
			{"placeholder": "cost_category_label", "label": "Categoria de custo (nome legível)", "loop_only": True, "loop_var": "s"},
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
		"condicional_motivo": "Campos dentro de {% for p in s.payments %}",
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
		"grupo": "Protocolo",
		"condicional": True,
		"condicional_motivo": "Quando um protocolo é selecionado no diálogo Gerar Documentos",
		"items": [
			{"placeholder": "permit_name", "label": "Código do protocolo"},
			{"placeholder": "permit_title", "label": "Título do protocolo"},
			{"placeholder": "permit_number", "label": "Número do protocolo"},
			{"placeholder": "permit_type", "label": "Tipo de protocolo (código Link)"},
			{"placeholder": "permit_type_label", "label": "Tipo de protocolo (nome legível)"},
			{"placeholder": "permit_status", "label": "Status"},
			{"placeholder": "permit_protocol_date", "label": "Data do protocolo"},
			{"placeholder": "permit_expiry_date", "label": "Data de validade"},
			{"placeholder": "permit_responsible_professional", "label": "Responsável técnico (ART/RRT)"},
			{"placeholder": "permit_crea_cau_number", "label": "Nº CREA/CAU do protocolo"},
			{"placeholder": "permit_art_rrt_number", "label": "Nº ART/RRT do protocolo"},
			{"placeholder": "permit_art_validity_date", "label": "Validade da ART/RRT"},
			{"placeholder": "permit_art_fee", "label": "Taxa ART/RRT (R$)"},
			{"placeholder": "permit_art_fee_fmt", "label": "Taxa ART/RRT (formatada)"},
			{"placeholder": "permit_agency", "label": "Órgão público"},
		],
	},
	{
		"grupo": "Contrato",
		"condicional": True,
		"condicional_motivo": "Refere-se a UM contrato (selecionado na geração, ou o contrato principal da obra). Diferente de project_current_contract_value, que é a soma de todos os contratos.",
		"items": [
			{"placeholder": "contract_name", "label": "Código do contrato"},
			{"placeholder": "contract_title", "label": "Título do contrato"},
			{"placeholder": "contract_status", "label": "Status do contrato"},
			{"placeholder": "contract_base_value", "label": "Valor base (R$)"},
			{"placeholder": "contract_base_value_fmt", "label": "Valor base (formatado)"},
			{"placeholder": "contract_value", "label": "Valor atual (R$)"},
			{"placeholder": "contract_value_fmt", "label": "Valor atual (formatado)"},
			{"placeholder": "contract_value_words", "label": "Valor atual por extenso"},
			{"placeholder": "contract_adjustment_index", "label": "Índice de reajuste"},
			{"placeholder": "contract_technical_retention_pct", "label": "Retenção técnica (%)"},
			{"placeholder": "contract_late_fee_pct", "label": "Multa mora (%)"},
			{"placeholder": "contract_daily_interest_pct", "label": "Juros diários (%)"},
			{"placeholder": "contract_monthly_interest_pct", "label": "Juros mensais (%)"},
			{"placeholder": "contract_installment_count", "label": "Número de parcelas"},
			{"placeholder": "contract_first_installment_date", "label": "Data da 1ª parcela"},
			{"placeholder": "contract_installment_value", "label": "Valor médio da parcela (R$)"},
			{"placeholder": "contract_installment_value_fmt", "label": "Valor médio da parcela (formatado)"},
			{"placeholder": "contract_total_received", "label": "Total recebido (R$)"},
			{"placeholder": "contract_total_received_fmt", "label": "Total recebido (formatado)"},
			{"placeholder": "contract_total_outstanding", "label": "Saldo a receber (R$)"},
			{"placeholder": "contract_total_outstanding_fmt", "label": "Saldo a receber (formatado)"},
			{"placeholder": "contract_observations", "label": "Observações do contrato"},
			{
				"placeholder": "contract_installments",
				"label": "Lista de parcelas (use {% for i in contract_installments %})",
			},
			{"placeholder": "contract_payment_narrative", "label": "Narrativa de pagamento (texto gerado)"},
		],
	},
	{
		"grupo": "Parcela do contrato (loop)",
		"condicional": True,
		"condicional_motivo": "Campos dentro de {% for i in contract_installments %}",
		"items": [
			{"placeholder": "payment_condition", "label": "Condição de pagamento", "loop_only": True, "loop_var": "i"},
			{"placeholder": "due_date", "label": "Vencimento", "loop_only": True, "loop_var": "i"},
			{"placeholder": "due_date_fmt", "label": "Vencimento (formatado)", "loop_only": True, "loop_var": "i"},
			{"placeholder": "amount", "label": "Valor previsto (R$)", "loop_only": True, "loop_var": "i"},
			{"placeholder": "amount_fmt", "label": "Valor previsto (formatado)", "loop_only": True, "loop_var": "i"},
			{"placeholder": "received_amount", "label": "Valor recebido (R$)", "loop_only": True, "loop_var": "i"},
			{"placeholder": "received_amount_fmt", "label": "Valor recebido (formatado)", "loop_only": True, "loop_var": "i"},
			{"placeholder": "status", "label": "Status", "loop_only": True, "loop_var": "i"},
			{"placeholder": "description", "label": "Descrição", "loop_only": True, "loop_var": "i"},
			{"placeholder": "receipt_date", "label": "Data de recebimento", "loop_only": True, "loop_var": "i"},
			{"placeholder": "receipt_date_fmt", "label": "Data de recebimento (formatada)", "loop_only": True, "loop_var": "i"},
			{"placeholder": "nf_number", "label": "Nº nota fiscal", "loop_only": True, "loop_var": "i"},
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


# Guia de uso (tutoriais) exibido pelo botão "Como usar os placeholders".
# Cada seção: titulo, descricao e lista de exemplos {codigo, resultado, nota}.
PLACEHOLDER_GUIDE = [
	{
		"titulo": "1. Sintaxe básica",
		"descricao": "Insira o nome do campo entre chaves duplas. O sistema substitui pelo valor da obra ao gerar o .docx.",
		"exemplos": [
			{
				"codigo": "Cliente: {{ customer_name }}",
				"resultado": "Cliente: Construtora Exemplo Ltda",
				"nota": "Texto simples. Use a lista 'Ver Placeholders Disponíveis' para todos os campos.",
			},
			{
				"codigo": "Obra {{ project }} — {{ project_city }}/{{ project_address_uf }}",
				"resultado": "Obra PROJ-2026-0278 — São Leopoldo/RS",
				"nota": "Vários placeholders no mesmo parágrafo.",
			},
		],
	},
	{
		"titulo": "2. Valores: bruto x formatado (_fmt)",
		"descricao": "Todo valor numérico tem duas formas: o bruto (número puro, para cálculo) e o _fmt (texto já formatado em padrão BR, para exibir).",
		"exemplos": [
			{
				"codigo": "Valor: R$ {{ contract_value_fmt }}",
				"resultado": "Valor: R$ 5.200.000,00",
				"nota": "Use _fmt para exibir direto. Já vem com milhar '.' e decimal ','.",
			},
			{
				"codigo": "{{ contract_value }}",
				"resultado": "5200000.0",
				"nota": "O bruto NÃO é formatado — use apenas em cálculos, não para exibir.",
			},
		],
	},
	{
		"titulo": "3. Cálculos com formatação BR (filtros real / num_br)",
		"descricao": "Para calcular e exibir em padrão BR, faça a conta com os valores BRUTOS e aplique o filtro 'real' (moeda) ou 'num_br' (número). Também funciona como função: real(...).",
		"exemplos": [
			{
				"codigo": "Valor unitário: R$ {{ (contract_base_value / project_construction_area) | real }}/m²",
				"resultado": "Valor unitário: R$ 1.083,33/m²",
				"nota": "Filtro 'real' = moeda. Calcule com o bruto; o filtro formata o resultado.",
			},
			{
				"codigo": "Área: {{ project_construction_area | num_br }} m²",
				"resultado": "Área: 4.800,00 m²",
				"nota": "Filtro 'num_br' (= 'numero') para áreas/quantidades. Escreva 'm²' no texto.",
			},
			{
				"codigo": "Total com taxa: R$ {{ real(contract_base_value * 1.1) }}",
				"resultado": "Total com taxa: R$ 5.720.000,00",
				"nota": "Forma de função: real(...) e num_br(...). Apelidos: real=moeda, num_br=numero.",
			},
		],
	},
	{
		"titulo": "4. Listas (loops) — orçamento, parcelas, subcontratos",
		"descricao": "Use {% for ... %} ... {% endfor %} para repetir linhas. Dentro do loop, acesse os campos pela variável do item.",
		"exemplos": [
			{
				"codigo": "{% for item in project_items %}\n{{ item.title }} — {{ item.total_value_fmt }}\n{% endfor %}",
				"resultado": "Concreto FCK30 — 11.106,00\nAço CA-50 — 4.200,00",
				"nota": "Itens do orçamento (revisão vigente). Cada item já traz _fmt.",
			},
			{
				"codigo": "{% for i in contract_installments %}\n{{ i.due_date_fmt }}: {{ i.amount_fmt }} ({{ i.status }})\n{% endfor %}",
				"resultado": "01/09/2025: 520.000,00 (Recebido)\n01/12/2025: 520.000,00 (Pendente)",
				"nota": "Parcelas do contrato selecionado.",
			},
			{
				"codigo": "{% for s in subcontracts %}\n{{ s.supplier_name }}: {{ s.total_value_fmt }}\n{% endfor %}",
				"resultado": "João Pedreiro: 5.000,00",
				"nota": "Subcontratos da obra. Para tabelas Word, coloque o for na linha da tabela.",
			},
		],
	},
	{
		"titulo": "5. Condicionais (mostrar só quando houver valor)",
		"descricao": "Use {% if %} para exibir trechos apenas quando o campo estiver preenchido.",
		"exemplos": [
			{
				"codigo": "{% if project_art_number %}ART nº {{ project_art_number }}{% endif %}",
				"resultado": "ART nº 1234567",
				"nota": "Se vazio, nada é impresso.",
			},
			{
				"codigo": "{% if contract_name %}Contrato {{ contract_name }} no valor de R$ {{ contract_value_fmt }}.{% else %}Obra sem contrato.{% endif %}",
				"resultado": "Contrato CNTR-2026-0317 no valor de R$ 5.200.000,00.",
				"nota": "if/else para textos alternativos.",
			},
		],
	},
	{
		"titulo": "6. Contrato: um contrato x soma da obra",
		"descricao": "Os campos 'contract_*' referem-se a UM contrato (o selecionado ao gerar, ou o contrato principal). Já 'project_current_contract_value' é a SOMA de todos os contratos da obra.",
		"exemplos": [
			{
				"codigo": "Valor deste contrato: R$ {{ contract_value_fmt }}",
				"resultado": "Valor deste contrato: R$ 5.200.000,00",
				"nota": "Em documentos contratuais, use contract_value_fmt.",
			},
			{
				"codigo": "Total contratado na obra: R$ {{ project_current_contract_value_fmt }}",
				"resultado": "Total contratado na obra: R$ 6.700.000,00",
				"nota": "Soma de todos os contratos — use só quando quiser o total da obra.",
			},
		],
	},
	{
		"titulo": "7. Datas, valor por extenso e logotipo",
		"descricao": "Datas têm versão _fmt (dd/mm/aaaa). O valor do contrato tem versão por extenso. O logotipo é a URL configurada no Escritório.",
		"exemplos": [
			{
				"codigo": "São Leopoldo, {{ today }}.",
				"resultado": "São Leopoldo, 29/06/2026.",
				"nota": "'today' já vem formatado. Datas de campos usam _fmt (ex.: contract_first_installment_date).",
			},
			{
				"codigo": "Valor de R$ {{ contract_value_fmt }} ({{ contract_value_words }}).",
				"resultado": "Valor de R$ 5.200.000,00 (cinco milhões e duzentos mil reais).",
				"nota": "contract_value_words = valor por extenso.",
			},
		],
	},
]


@frappe.whitelist()
def generate_project_documents(
	project_name: str,
	template_names: str | list,
	permit_name: str | None = None,
	contract_name: str | None = None,
) -> dict:
	frappe.has_permission("Construction Project", "write", doc=project_name, throw=True)
	names = _parse_template_names(template_names)
	if not names:
		frappe.throw(_("Selecione ao menos um template."))

	context = _build_context(project_name, permit_name=permit_name, contract_name=contract_name)
	generated = []
	failures = []

	for template_name in names:
		try:
			template_doc = frappe.get_doc("Document Template", template_name)
			if not template_doc.enabled:
				raise frappe.ValidationError(_("Template desabilitado: {0}").format(template_name))
			result = _render_document(project_name, template_doc, context)
			generated.append(
				{
					"template": template_name,
					"title": template_doc.template_name,
					"file_name": result["file_name"],
					"file_content": base64.b64encode(result["content"]).decode("ascii"),
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
def get_project_contracts(project_name: str) -> list[dict]:
	frappe.has_permission("Engineering Contract", "read", throw=True)
	return frappe.get_all(
		"Engineering Contract",
		filters={"project": project_name, "status": ["!=", "Cancelado"]},
		fields=["name", "title", "status", "is_primary", "current_value"],
		order_by="is_primary desc, modified desc",
		limit_page_length=0,
	)


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


@frappe.whitelist()
def get_placeholder_guide() -> list[dict]:
	frappe.has_permission("Document Template", "read", throw=True)
	return PLACEHOLDER_GUIDE


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


# Documentos contratuais devem sair sempre em padrão BR (milhar "." e decimal ","),
# independente do number_format do site onde o app está instalado.
_BR_NUMBER_FORMAT = "#.###,##"


def _fmt_currency(value) -> str:
	return fmt_money(flt(value), format=_BR_NUMBER_FORMAT)


def _fmt_number(value, precision: int = 2) -> str:
	return fmt_money(flt(value), precision=precision, format=_BR_NUMBER_FORMAT)


def _value_in_words(value) -> str:
	"""Converte valor numérico para texto por extenso em PT-BR (moeda)."""
	amount = flt(value)
	if not amount:
		return ""
	try:
		return _num2words(amount, lang="pt_BR", to="currency")
	except Exception:
		return ""


def _get_settings_context(settings) -> dict:
	return {
		"company_name": settings.company_name or "",
		"company_cnpj": formatar_cnpj(settings.company_cnpj) if settings.company_cnpj else "",
		"company_crea": settings.company_crea or "",
		"company_logo": settings.company_logo or "",
		"company_address_full": settings.company_address_full or "",
		"bank_name": settings.bank_name or "",
		"bank_agency": settings.bank_agency or "",
		"bank_account": settings.bank_account or "",
		"bank_pix": settings.bank_pix or "",
		"engineer_full_name": settings.engineer_full_name or "",
		"engineer_cpf": formatar_cpf(settings.engineer_cpf) if settings.engineer_cpf else "",
		"engineer_phone": formatar_telefone(settings.engineer_phone) if settings.engineer_phone else "",
		"engineer_email": (settings.engineer_email or "").lower(),
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
		"customer_cpf": formatar_cpf(customer.cpf) if customer and customer.cpf else "",
		"customer_cnpj": formatar_cnpj(customer.cnpj) if customer and customer.cnpj else "",
		"customer_rg": customer.rg if customer and customer.rg else "",
		"customer_rg_issuer": customer.rg_issuer if customer and customer.rg_issuer else "",
		"customer_birth_date": _fmt_date(customer.birth_date) if customer and customer.birth_date else "",
		"customer_birth_date_fmt": _fmt_date(customer.birth_date) if customer and customer.birth_date else "",
		"cpf": formatar_cpf(customer.cpf) if customer and customer.cpf else "",
		"cnpj": formatar_cnpj(customer.cnpj) if customer and customer.cnpj else "",
		"rg": customer.rg if customer and customer.rg else "",
		"customer_trade_name": customer.trade_name if customer and customer.trade_name else "",
		"customer_nationality": customer.nationality if customer and customer.nationality else "",
		"customer_marital_status": customer.marital_status if customer and customer.marital_status else "",
		"customer_profession": customer.profession if customer and customer.profession else "",
		"customer_legal_representative": (customer.legal_representative or "") if customer else "",
		"customer_legal_representative_cpf": (
			formatar_cpf(customer.legal_representative_cpf) if customer and customer.legal_representative_cpf else ""
		),
		"customer_legal_representative_role": (customer.legal_representative_role or "") if customer else "",
		"customer_legal_representative_nationality": (customer.legal_representative_nationality or "") if customer else "",
		"customer_observations": strip_html(customer.observations or "") if customer else "",
		"address_street": addr.street if addr else "",
		"address_number": addr.number if addr else "",
		"address_complement": addr.complement if addr else "",
		"address_district": addr.district if addr else "",
		"address_city": addr.city if addr else "",
		"address_state": addr.state if addr else "",
		"address_cep": formatar_cep(addr.cep) if addr and addr.cep else "",
		"endereco": addr.street if addr else "",
		"numero": addr.number if addr else "",
		"bairro": addr.district if addr else "",
		"cidade": addr.city if addr else "",
		"estado": addr.state if addr else "",
		"cep": formatar_cep(addr.cep) if addr and addr.cep else "",
		"address_full": customer_address_full,
		"contact_name": contact.contact_name if contact else "",
		"contact_phone": formatar_telefone(contact.phone) if contact and contact.phone else "",
		"contact_mobile": formatar_telefone(contact.mobile) if contact and contact.mobile else "",
		"contact_email": (contact.email or "").lower() if contact and contact.email else "",
		"telefone": formatar_telefone(contact.phone) if contact and contact.phone else "",
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
		"project_address_cep": formatar_cep(project.address_cep) if project.address_cep else "",
		"project_address_full": project_address_full,
		"project_location_code": project.location_code or "",
		"project_dic": project.dic or "",
		"project_construction_area": flt(project.construction_area),
		"project_construction_area_fmt": _fmt_number(project.construction_area),
		"project_current_contract_value": current_contract_value,
		"project_current_contract_value_fmt": _fmt_currency(current_contract_value),
		"project_physical_progress": flt(project.physical_progress),
		"project_physical_progress_fmt": _fmt_number(project.physical_progress),
		"project_responsible_engineer": project.responsible_engineer or "",
		"project_crea_number": project.crea_number or "",
		"project_art_number": project.art_number or "",
		"project_art_execution_number": project.art_execution_number or "",
		"project_building_type": project.building_type or "",
		"project_building_type_label": project.building_type or "",
		"project_main_material": project.main_material or "",
		"project_unit_count": project.unit_count or 0,
		"project_estimated_population": project.estimated_population or 0,
		"project_occupancy_permit": project.occupancy_permit or "",
		"project_structural_engineer": project.structural_engineer or "",
		"project_structural_company": project.structural_company or "",
		"project_structural_engineer_crea": project.structural_engineer_crea or "",
		"project_structural_art_number": project.structural_art_number or "",
		"project_property_registration": project.property_registration or "",
		"project_gps_coordinates": project.gps_coordinates or "",
		"project_budget_revision": project.budget_revision or 1,
		"project_default_bdi_percent": flt(project.default_bdi_percent),
		"project_default_bdi_percent_fmt": _fmt_number(project.default_bdi_percent),
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

	cost_category_labels = {}
	cost_categories = {row.cost_category for row in rows if row.cost_category}
	if cost_categories:
		for cat_row in frappe.get_all(
			"Cost Category",
			filters={"name": ["in", list(cost_categories)]},
			fields=["name", "category_name"],
			limit=100,
		):
			cost_category_labels[cat_row.name] = cat_row.category_name or cat_row.name

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
				"supplier_cnpj": formatar_cnpj(supplier_cnpjs.get(row.supplier, ""))
				if supplier_cnpjs.get(row.supplier)
				else "",
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
				"cost_category_label": cost_category_labels.get(row.cost_category, row.cost_category or ""),
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


def _count_in_words(n: int) -> str:
	"""Número cardinal feminino para contagem de parcelas (uma, duas, três...)."""
	if n == 1:
		return "uma"
	if n == 2:
		return "duas"
	return _num2words(n, lang="pt_BR")


def _build_payment_narrative(installments: list[dict]) -> str:
	"""Monta narrativa jurídica agrupada a partir das parcelas processadas.

	Agrupa parcelas 'Data fixa' consecutivas de mesmo valor e mesmo dia do mês.
	Trata a última parcela de um grupo como ajuste se diferir em ≤ 5% do valor padrão.
	Parcelas com condição diferente de 'Data fixa' geram frase individual.
	"""
	if not installments:
		return ""

	active = [row for row in installments if row.get("status") != "Cancelado"]
	if not active:
		return ""

	fixed = [
		row
		for row in active
		if (row.get("payment_condition") or "Data fixa") == "Data fixa" and row.get("due_date")
	]
	non_fixed = [row for row in active if row not in fixed]

	parts = []

	if fixed:
		groups = []
		current_group = [fixed[0]]

		for i in range(1, len(fixed)):
			prev_amount = flt(current_group[0]["amount"])
			curr_amount = flt(fixed[i]["amount"])
			amounts_match = abs(curr_amount - prev_amount) <= 0.02

			if amounts_match:
				current_group.append(fixed[i])
			else:
				is_last = i == len(fixed) - 1
				diff_pct = abs(curr_amount - prev_amount) / prev_amount * 100 if prev_amount else 100
				if is_last and diff_pct <= 5 and len(current_group) >= 2:
					current_group.append(fixed[i])
				else:
					groups.append(current_group)
					current_group = [fixed[i]]

		groups.append(current_group)

		for group in groups:
			count = len(group)
			main_amount = flt(group[0]["amount"])
			start_date = group[0]["due_date"]

			try:
				day = getdate(start_date).day
			except Exception:
				day = None

			last_amount = flt(group[-1]["amount"])
			has_adjustment = count > 1 and abs(last_amount - main_amount) > 0.02

			count_display = f"{count:02d}" if count < 100 else str(count)
			count_words = _count_in_words(count)
			amount_fmt = _fmt_currency(main_amount)
			amount_words = _value_in_words(main_amount)
			start_date_fmt = _fmt_date(start_date)

			if count == 1:
				line = f"{count_display} ({count_words}) parcela de {amount_fmt} ({amount_words})"
				if day:
					line += f", com vencimento em {start_date_fmt}"
			else:
				line = f"{count_display} ({count_words}) parcelas de {amount_fmt} ({amount_words})"
				line += " mensais e consecutivas"
				if day:
					line += f" com pagamento todo dia {day:02d}"
				line += f", a iniciar em {start_date_fmt}"

			if has_adjustment:
				adj_fmt = _fmt_currency(last_amount)
				adj_words = _value_in_words(last_amount)
				line += f", sendo a última parcela no valor de {adj_fmt} ({adj_words})"

			line += "."
			parts.append(line)

	condition_text = {
		"Na conclusão": "a ser paga na conclusão do serviço",
		"Na aprovação": "a ser paga na aprovação do projeto",
		"A definir": "com data a definir",
	}

	for row in non_fixed:
		amount = flt(row["amount"])
		amount_fmt = _fmt_currency(amount)
		amount_words = _value_in_words(amount)
		condition = row.get("payment_condition") or "A definir"
		suffix = condition_text.get(condition, "com data a definir")

		desc = row.get("description")
		if desc:
			line = f"01 (uma) parcela de {amount_fmt} ({amount_words}) referente a {desc.lower()}, {suffix}."
		else:
			line = f"01 (uma) parcela de {amount_fmt} ({amount_words}), {suffix}."

		parts.append(line)

	return "\n\n".join(parts)


def _installment_due_date_sort_key(due_date) -> tuple:
	"""Ordena parcelas por vencimento; vazias por último; normaliza str/date."""
	if not due_date:
		return (1, getdate("9999-12-31"))
	return (0, getdate(due_date))


def _get_contract_installment_row(installment) -> dict:
	amount = flt(installment.amount)
	received_amount = flt(installment.received_amount)
	return {
		"payment_condition": installment.payment_condition or "Data fixa",
		"due_date": installment.due_date or "",
		"due_date_fmt": _fmt_date(installment.due_date),
		"amount": amount,
		"amount_fmt": _fmt_currency(amount),
		"received_amount": received_amount,
		"received_amount_fmt": _fmt_currency(received_amount),
		"status": installment.status or "",
		"description": installment.description or "",
		"receipt_date": installment.receipt_date or "",
		"receipt_date_fmt": _fmt_date(installment.receipt_date),
		"nf_number": installment.nf_number or "",
	}


def _get_contract_context(contract) -> dict:
	empty = {
		"contract_name": "",
		"contract_title": "",
		"contract_status": "",
		"contract_base_value": 0,
		"contract_base_value_fmt": _fmt_currency(0),
		"contract_value": 0,
		"contract_value_fmt": _fmt_currency(0),
		"contract_value_words": "",
		"contract_adjustment_index": "",
		"contract_technical_retention_pct": 0,
		"contract_late_fee_pct": 0,
		"contract_daily_interest_pct": 0,
		"contract_monthly_interest_pct": 0,
		"contract_installment_count": 0,
		"contract_first_installment_date": "",
		"contract_installment_value": 0,
		"contract_installment_value_fmt": _fmt_currency(0),
		"contract_total_received": 0,
		"contract_total_received_fmt": _fmt_currency(0),
		"contract_total_outstanding": 0,
		"contract_total_outstanding_fmt": _fmt_currency(0),
		"contract_observations": "",
		"contract_installments": [],
		"contract_payment_narrative": "",
	}

	if not contract:
		return empty

	base_value = flt(contract.base_value)
	current_value = flt(contract.current_value)
	installment_value = flt(contract.installment_value)
	installments = [
		_get_contract_installment_row(row)
		for row in sorted(
			contract.installments or [],
			key=lambda row: _installment_due_date_sort_key(row.due_date),
		)
	]
	total_received = sum(flt(row.get("received_amount")) for row in installments)
	total_outstanding = sum(
		max(0, flt(row.get("amount")) - flt(row.get("received_amount")))
		for row in installments
		if row.get("status") not in ("Cancelado",)
	)
	return {
		"contract_name": contract.name,
		"contract_title": contract.title or contract.name,
		"contract_status": contract.status or "",
		"contract_base_value": base_value,
		"contract_base_value_fmt": _fmt_currency(base_value),
		"contract_value": current_value,
		"contract_value_fmt": _fmt_currency(current_value),
		"contract_value_words": _value_in_words(current_value),
		"contract_adjustment_index": contract.adjustment_index or "",
		"contract_technical_retention_pct": flt(contract.technical_retention_pct),
		"contract_late_fee_pct": flt(contract.late_fee_pct),
		"contract_daily_interest_pct": flt(contract.daily_interest_pct),
		"contract_monthly_interest_pct": flt(contract.monthly_interest_pct),
		"contract_installment_count": contract.installment_count or len(installments),
		"contract_first_installment_date": _fmt_date(contract.first_installment_date),
		"contract_installment_value": installment_value,
		"contract_installment_value_fmt": _fmt_currency(installment_value),
		"contract_total_received": total_received,
		"contract_total_received_fmt": _fmt_currency(total_received),
		"contract_total_outstanding": total_outstanding,
		"contract_total_outstanding_fmt": _fmt_currency(total_outstanding),
		"contract_observations": strip_html(contract.observations or ""),
		"contract_installments": installments,
		"contract_payment_narrative": _build_payment_narrative(installments),
	}


def _get_permit_context(permit_name: str | None) -> dict:
	empty = {
		"permit_name": "",
		"permit_title": "",
		"permit_number": "",
		"permit_type": "",
		"permit_type_label": "",
		"permit_status": "",
		"permit_protocol_date": "",
		"permit_expiry_date": "",
		"permit_responsible_professional": "",
		"permit_crea_cau_number": "",
		"permit_art_rrt_number": "",
		"permit_art_validity_date": "",
		"permit_art_fee": 0,
		"permit_art_fee_fmt": _fmt_currency(0),
		"permit_agency": "",
	}
	if not permit_name:
		return empty

	permit = frappe.get_doc("Permit", permit_name)
	agency_name = ""
	if permit.public_agency:
		agency_name = frappe.db.get_value("Public Agency", permit.public_agency, "agency_name") or permit.public_agency
	permit_type_label = ""
	if permit.permit_type:
		permit_type_label = (
			frappe.db.get_value("Permit Type", permit.permit_type, "type_name") or permit.permit_type
		)
	art_fee = flt(permit.art_fee)

	return {
		"permit_name": permit.name,
		"permit_title": permit.title or permit.name,
		"permit_number": permit.permit_number or "",
		"permit_type": permit.permit_type or "",
		"permit_type_label": permit_type_label,
		"permit_status": permit.status or "",
		"permit_protocol_date": _fmt_date(permit.protocol_date),
		"permit_expiry_date": _fmt_date(permit.expiry_date),
		"permit_responsible_professional": permit.responsible_professional or "",
		"permit_crea_cau_number": permit.crea_cau_number or "",
		"permit_art_rrt_number": permit.art_rrt_number or "",
		"permit_art_validity_date": _fmt_date(permit.art_validity_date),
		"permit_art_fee": art_fee,
		"permit_art_fee_fmt": _fmt_currency(art_fee),
		"permit_agency": agency_name,
	}


# Prioridade do fallback quando a obra não tem contrato principal definido.
_CONTRACT_STATUS_PRIORITY = ("Vigente", "Quitado", "Encerrado")


def _resolve_contract(project_name: str, contract_name: str | None = None):
	"""Resolve o contrato da obra: explícito > principal > fallback determinístico."""
	if contract_name:
		info = frappe.db.get_value(
			"Engineering Contract", contract_name, ["project", "status"], as_dict=True
		)
		if not info or info.project != project_name:
			frappe.throw(_("O contrato selecionado não pertence a esta obra."))
		if info.status == "Cancelado":
			frappe.throw(_("O contrato selecionado está cancelado."))
		return frappe.get_doc("Engineering Contract", contract_name)

	primary = frappe.db.get_value(
		"Engineering Contract",
		{"project": project_name, "is_primary": 1, "status": ["!=", "Cancelado"]},
		"name",
	)
	if primary:
		return frappe.get_doc("Engineering Contract", primary)

	rows = frappe.get_all(
		"Engineering Contract",
		filters={"project": project_name, "status": ["!=", "Cancelado"]},
		fields=["name", "status", "modified"],
		limit_page_length=0,
	)
	if not rows:
		return None

	def _status_priority(status: str) -> int:
		try:
			return _CONTRACT_STATUS_PRIORITY.index(status)
		except ValueError:
			return len(_CONTRACT_STATUS_PRIORITY)

	rows.sort(key=lambda row: row.modified or "", reverse=True)
	rows.sort(key=lambda row: _status_priority(row.status))
	return frappe.get_doc("Engineering Contract", rows[0].name)


def _build_context(
	project_name: str, permit_name: str | None = None, contract_name: str | None = None
) -> dict:
	project = frappe.get_doc("Construction Project", project_name)
	customer = frappe.get_doc("Customer", project.customer) if project.customer else None
	addr = _primary_customer_address(customer)
	contact = _primary_customer_contact(customer)

	if permit_name:
		permit_project = frappe.db.get_value("Permit", permit_name, "project")
		if permit_project != project.name:
			frappe.throw(_("O protocolo selecionado não pertence a esta obra."))

	contract = _resolve_contract(project.name, contract_name)
	settings = frappe.get_single("Engineering Settings")

	context = {}
	context.update(_get_settings_context(settings))
	context.update(_get_customer_context(customer, addr, contact))
	context.update(_get_project_context(project))
	context.update(_get_project_items_context(project.name))
	context.update(_get_contract_context(contract))
	context.update(_get_subcontracts_context(project.name))
	context.update(_get_permit_context(permit_name))
	context.update(
		{
			"today": formatdate(today()),
			"today_iso": getdate(today()).isoformat(),
		}
	)
	context.update(_document_format_helpers())
	return context


def _document_format_helpers() -> dict:
	"""Funções de formatação BR usáveis no template (ex.: {{ real(valor / area) }})."""
	return {
		"real": _fmt_currency,
		"moeda": _fmt_currency,
		"num_br": _fmt_number,
		"numero": _fmt_number,
	}


def _document_jinja_env():
	"""Motor Jinja do docxtpl com filtros BR (ex.: {{ (valor / area) | real }})."""
	import jinja2

	env = jinja2.Environment(autoescape=False)
	env.filters["real"] = _fmt_currency
	env.filters["moeda"] = _fmt_currency
	env.filters["num_br"] = _fmt_number
	env.filters["numero"] = _fmt_number
	return env


def _infer_document_category(template_doc) -> str:
	search_text = " ".join(
		part
		for part in (
			template_doc.template_name,
			template_doc.document_type,
			template_doc.description,
		)
		if part
	).lower()
	for keyword, category in TEMPLATE_CATEGORY_MAP.items():
		if keyword in search_text:
			return category
	return "Outro"


def _render_docx_template(template_doc, context: dict) -> bytes:
	"""Renderiza o .docx de um Document Template com o contexto Jinja BR.

	Núcleo reutilizável: carrega o arquivo do template, aplica o motor Jinja
	com filtros BR e retorna os bytes do documento gerado.

	Args:
		template_doc: doc do Document Template (precisa de document_file).
		context: dicionário de variáveis Jinja.

	Returns:
		bytes do .docx renderizado.
	"""
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
	tpl.render(context, _document_jinja_env())

	buffer = io.BytesIO()
	tpl.save(buffer)
	buffer.seek(0)
	return buffer.read()


def _render_document(project_name, template_doc, context):
	content = _render_docx_template(template_doc, context)

	category = _infer_document_category(template_doc)
	file_name = compose_project_document_filename(
		project_name,
		category,
		"v1",
		template_doc.template_name,
		".docx",
	)

	return {"file_name": file_name, "content": content}
