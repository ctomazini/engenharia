# CODEBASE — App Engenharia (Frappe v16)

> Gerado em **2026-06-29** — inventário técnico do app greenfield EN. Frappe puro, **sem ERPNext**.

> **HEAD:** `6f43c31 2026-06-29 23:13:07 +0000 feat: add receivables report button to eng-dashboard financial tab`

---

## 1. Visão Geral

| Item | Valor |
| --- | --- |
| Nome | engenharia |
| Versão | 1.3.0 (`pyproject.toml`) |
| Framework | Frappe v16 |
| Licença | MIT |
| Site dev | engenharia.local |
| Linhas Python | ~20248 |
| Linhas JavaScript | ~7490 |
| Métodos de teste | 344 (61 arquivos) |
| DocTypes | 49 (`custom: 0`) |
| Script Reports | 6 |
| Print Formats | 15 |

**Propósito:** gestão de obras — projetos, contratos, custos (obra + escritório), subcontratos, comissões, prazos, protocolos, pagamentos, painel modular, documentos `.docx`, impressão PDF de relatórios.

**Deps:** `docxtpl>=0.18.0`.

**Commits recentes:**
```text
6f43c31 feat: add receivables report button to eng-dashboard financial tab
fb7aa87 feat: add monthly receivables report generator for accountant
0ff6f0b chore(release): bump version to 1.2.0 and sync documentation
ee7f7aa feat(document-template): add "how to use placeholders" guide button
7c0d2a7 feat(documents): pt-BR jinja filters/functions for computed values
72069c7 fix(documents): force Brazilian number format on all value placeholders
47545b1 docs: clarify single contract vs project total in placeholders
cded271 feat(construction-project): contract selector in document dialog
d9cb5a2 feat(documents): resolve contract by explicit/primary/fallback
16af34b feat(patches): backfill primary contract for single-contract projects
113ffd0 feat(engineering-contract): add primary contract flag with uniqueness
87573e2 fix(documents): add pt-BR formatted variants for numeric placeholders
```

## 2. Árvore de Arquivos (anotada)

```text
engenharia/
├── CODEBASE.md, README.md, REGRAS_OBRIGATORIAS.md, pyproject.toml
└── engenharia/
    ├── hooks.py, boot.py, dashboard_api.py, agent_api.py, documents.py
    ├── financial.py, work_costs.py, report_visuals.py, titles.py, validators.py
    ├── dashboard/ (kpis, financial, budget_margin, deadlines, timeline, attention, health, …)
    ├── public/js/ (masks, list_nav, hub, reports_common, dashboard/*)
    ├── public/css/ (reports, hub, list_filters, sidebar_fix)
    ├── setup/ (install, sidebar, workspace, reports, print_formats, permissions, seed)
    ├── print_formats/reports/ (templates PDF Script Reports)
    └── engenharia/ (doctype/, report/, page/eng_dashboard/)
```

## 3. Script Reports

| Report | Pasta | Print formats |
| --- | --- | --- |
| work_cost_by_project | Compras avulsas por obra | Resumo |
| work_cost_by_category | Compras avulsas por categoria | Resumo |
| cash_flow | Fluxo de Caixa | Resumo + Paisagem |
| project_margin | Margem por Obra | Resumo + Paisagem |
| consolidated_cost | Custos Realizados | Resumo + Detalhado + Paisagem |
| budget_vs_actual | Orçado vs Realizado | Resumo + Paisagem |

## 4. Mapa de DocTypes

#### Standalone / transacionais

### Building Type

**Meta:** autoname=`field:building_type_name` · naming_rule=`By fieldname` · title_field=`building_type_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| building_type_name | Tipo de Edificação | Data |  | ✓ | ✓ |

### Commission

**Meta:** autoname=`format:CMSN-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| construction_project | Obra | Link | Construction Project | ✓ |  |
| commission_type | Tipo de Comissão | Select | Pré-Moldado Outro | ✓ |  |
| supplier_name | Fornecedor | Data |  | ✓ |  |
| supplier_tax_id | CNPJ do Fornecedor | Data |  |  |  |
| description | Descrição | Small Text |  |  |  |
| title | Título | Data |  |  |  |
| total_value | Valor Total | Currency |  | ✓ |  |
| total_paid | Total Pago | Currency |  |  |  |
| outstanding | Saldo a Receber | Currency |  |  |  |
| status | Status de Recebimento | Select | Open Partially Paid Paid Cancelled |  |  |
| payments | Recebimentos de Comissão | Table | Commission Payment |  |  |

### Communication Log

**Meta:** autoname=`format:COMM-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| title | Título | Data |  |  |  |
| project | Obra | Link | Construction Project |  |  |
| customer | Cliente | Link | Customer | ✓ |  |
| communication_date | Data | Datetime |  | ✓ |  |
| communication_type | Tipo | Select | Telefone WhatsApp Email Reunião Presencial Reunião Virtua... | ✓ |  |
| subject | Assunto | Data |  | ✓ |  |
| summary | Resumo | Text Editor |  |  |  |
| next_steps | Próximos Passos | Text Editor |  |  |  |
| create_task | Gerar Tarefa | Check |  |  |  |
| follow_up_date | Data de Follow-up | Date |  |  |  |
| task | Tarefa Gerada | Link | Task |  |  |

### Construction Measurement

**Meta:** autoname=`format:MED-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| form_help |  | HTML | <div class="form-message blue"><p><strong>Boletim de medi... |  |  |
| project | Obra | Link | Construction Project | ✓ |  |
| customer | Cliente | Link | Customer | ✓ |  |
| title | Título | Data |  |  |  |
| measurement_date | Data da medição | Date |  | ✓ |  |
| measurement_number | Medição Nº | Int |  |  |  |
| reference_period | Período de referência | Data |  |  |  |
| status | Status | Select | Rascunho Aprovada Contestada |  |  |
| measurement_items | Itens | Table | Construction Measurement Item | ✓ |  |
| total_measured_value | Total medido | Currency |  |  |  |
| observations | Observações | Text Editor |  |  |  |
| attachment | Anexo | Attach |  |  |  |

### Construction Project

**Meta:** autoname=`format:PROJ-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| hub_summary_bar | Resumo da Obra | HTML |  |  |  |
| customer | Cliente | Link | Customer | ✓ |  |
| title | Título | Data |  |  |  |
| project_type | Tipo de Obra | Select | Residencial Comercial Industrial Infraestrutura Reforma O... |  |  |
| status | Status | Select | Orçamento Em andamento Paralisada Concluída Cancelada |  |  |
| start_date | Data de Início | Date |  |  |  |
| expected_delivery | Previsão de Entrega | Date |  |  |  |
| address_cep | CEP | Data |  |  |  |
| address_street | Logradouro | Data |  |  |  |
| address_number | Número | Data |  |  |  |
| address_district | Bairro | Data |  |  |  |
| city | Cidade | Data |  |  |  |
| address_uf | UF | Select | AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ ... |  |  |
| location_code | Código de Localização | Data |  |  |  |
| dic | DIC | Data |  |  |  |
| property_registration | Matrícula do Imóvel | Data |  |  |  |
| construction_area | Área Construída (m²) | Float |  |  |  |
| building_type | Tipo de Edificação | Link | Building Type |  |  |
| main_material | Material Principal | Data |  |  |  |
| unit_count | Nº de Economias | Int |  |  |  |
| estimated_population | População Estimada | Int |  |  |  |
| occupancy_permit | Nº Habite-se | Data |  |  |  |
| responsible_engineer | Responsável Técnico | Data |  |  |  |
| crea_number | CREA do Responsável | Data |  |  |  |
| art_number | Nº ART Principal | Data |  |  |  |
| art_execution_number | Nº ART de Execução | Data |  |  |  |
| gps_coordinates | Coordenadas GPS | Data |  |  |  |
| structural_engineer | Responsável Técnico Estrutura | Data |  |  |  |
| structural_company | Empresa Estrutural | Data |  |  |  |
| structural_engineer_crea | CREA Estrutural | Data |  |  |  |
| structural_art_number | Nº ART Estrutural | Data |  |  |  |
| physical_progress | Avanço Físico Global | Percent |  |  |  |
| current_contract_value | Valor Atual do Contrato | Currency |  |  |  |
| commission_outstanding | Comissões a Receber | Currency |  |  |  |
| commission_summary_panel | Resumo de comissões | HTML | <p class="text-muted">Carregando comissões...</p> |  |  |
| budget_revision | Revisão vigente | Int |  |  |  |
| default_bdi_percent | BDI padrão % | Percent |  |  |  |
| stages_panel | Painel de Etapas | HTML | <p class="text-muted">Carregando etapas...</p> |  |  |
| budget_revisions | Revisões de orçamento | Table | Project Budget Revision |  |  |
| financial_summary_panel | Resumo Financeiro | HTML | <p class="text-muted">Carregando resumo...</p> |  |  |
| installments_panel | Parcelas do Contrato | HTML | <p class="text-muted">Plano de vencimentos do contrato. A... |  |  |
| costs_panel | Custos Realizados | HTML | <p class="text-muted">Compras avulsas, subcontratos e ree... |  |  |
| payments_panel | Recebimentos | HTML |  |  |  |
| reimbursables_panel | Despesas Reembolsáveis | HTML | <p class="text-muted">Despesas pagas pelo escritório a se... |  |  |
| commissions_hub_panel | Comissões | HTML |  |  |  |
| deadlines_panel | Prazos | HTML | <p class="text-muted">Carregando prazos...</p> |  |  |
| permits_panel | Alvarás e Protocolos | HTML | <p class="text-muted">Carregando alvarás e protocolos...</p> |  |  |
| tasks_panel | Tarefas | HTML | <p class="text-muted">Carregando tarefas...</p> |  |  |
| communications_panel | Comunicações | HTML | <p class="text-muted">Carregando comunicações...</p> |  |  |
| measurements_panel | Medições | HTML | <p class="text-muted">Carregando medições...</p> |  |  |
| timelogs_panel | Horas Trabalhadas | HTML | <p class="text-muted">Carregando horas...</p> |  |  |
| documents_panel | Documentos da Obra | HTML | <p class="text-muted">Carregando documentos...</p> |  |  |
| specs_help | Itens do Orçamento | HTML | <p class="text-muted">Use <b>Adicionar item do orçamento<... |  |  |
| spec_preview_panel | Prévia do Orçamento | HTML | <p class="text-muted">Carregando prévia...</p> |  |  |
| spec_items_summary_panel | Itens do Orçamento | HTML | <p class="text-muted">Carregando itens do orçamento...</p> |  |  |
| spec_project_total | Total do Orçamento | Currency |  |  |  |
| observations | Observações | Text Editor |  |  |  |

### Customer

**Meta:** autoname=`format:CLI-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`customer_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| person_type | Tipo de Pessoa | Select | Pessoa Física Pessoa Jurídica | ✓ |  |
| customer_name | Nome / Razão Social | Data |  | ✓ |  |
| trade_name | Nome Fantasia | Data |  |  |  |
| cpf | CPF | Data |  |  | ✓ |
| rg | RG | Data |  |  |  |
| rg_issuer | Órgão Emissor do RG | Data |  |  |  |
| cnpj | CNPJ | Data |  |  | ✓ |
| nationality | Nacionalidade | Data |  |  |  |
| marital_status | Estado Civil | Select |  Solteiro(a) Casado(a) Divorciado(a) Viúvo(a) União Estável |  |  |
| profession | Profissão | Data |  |  |  |
| birth_date | Data de Nascimento | Date |  |  |  |
| legal_representative | Representante Legal | Data |  |  |  |
| legal_representative_cpf | CPF do Representante | Data |  |  |  |
| legal_representative_role | Cargo | Data |  |  |  |
| legal_representative_nationality | Nacionalidade do Representante | Data |  |  |  |
| contacts | Contatos | Table | Customer Contact |  |  |
| addresses | Endereços | Table | Customer Address |  |  |
| observations | Observações | Text Editor |  |  |  |

### Deadline

**Meta:** autoname=`format:DLNE-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| title | Título | Data |  |  |  |
| project | Obra | Link | Construction Project | ✓ |  |
| customer | Cliente | Link | Customer |  |  |
| due_date | Data do Prazo | Date |  | ✓ |  |
| status | Status | Select | Pendente Concluído Vencido |  |  |
| deadline_type | Tipo de Prazo | Select | Projeto Cliente Órgão Outro |  |  |
| public_agency | Órgão Público | Link | Public Agency |  |  |
| description | Descrição | Small Text |  | ✓ |  |
| priority | Prioridade | Select | Alta Média Baixa |  |  |
| assigned_to | Responsável | Link | User |  |  |
| notify_days_before | Notificar com antecedência (dias) | Int |  |  |  |
| notes | Observações | Text Editor |  |  |  |

### Document Category

**Meta:** autoname=`field:category_name` · naming_rule=`By fieldname` · title_field=`category_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| category_name | Categoria | Data |  | ✓ | ✓ |

### Document Kit

**Meta:** autoname=`field:kit_name` · naming_rule=`By fieldname` · title_field=`kit_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| kit_name | Nome do kit | Data |  | ✓ | ✓ |
| description | Descrição | Small Text |  |  |  |
| enabled | Habilitado | Check |  |  |  |
| templates | Modelos de documento | Table | Document Kit Item | ✓ |  |

### Document Template

**Meta:** autoname=`field:template_name` · naming_rule=`By fieldname` · title_field=`template_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| form_help |  | HTML | <div class="form-message blue"><p>Modelos Word (.docx) co... |  |  |
| template_name | Nome do Template | Data |  | ✓ | ✓ |
| document_type | Tipo | Select | Contrato Proposta Relatório Outro |  |  |
| description | Descrição | Small Text |  |  |  |
| document_file | Arquivo .docx | Attach |  | ✓ |  |
| enabled | Habilitado | Check |  |  |  |
| view_placeholders | Ver Placeholders Disponíveis | Button |  |  |  |
| view_placeholder_guide | Como Usar os Placeholders | Button |  |  |  |

### Engineering Contract

**Meta:** autoname=`format:CNTR-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| project | Obra | Link | Construction Project | ✓ |  |
| customer | Cliente | Link | Customer | ✓ |  |
| title | Título | Data |  |  |  |
| status | Status | Select | Vigente Encerrado Cancelado Quitado |  |  |
| is_primary | Contrato Principal | Check |  |  |  |
| base_value | Valor Base | Currency |  | ✓ |  |
| current_value | Valor Atual | Currency |  |  |  |
| adjustment_index | Índice de Reajuste | Select |  INCC IPCA IGP-M Nenhum |  |  |
| technical_retention_pct | Retenção Técnica % | Percent |  |  |  |
| late_fee_pct | Multa Mora % | Percent |  |  |  |
| daily_interest_pct | Juros Diários % | Float |  |  |  |
| monthly_interest_pct | Juros Mensais (%) | Percent |  |  |  |
| installment_count | Número de Parcelas | Int |  |  |  |
| first_installment_date | Data da Primeira Parcela | Date |  |  |  |
| installment_value | Valor da Parcela | Currency |  |  |  |
| generate_installments | Gerar Parcelas | Button |  |  |  |
| installments | Parcelas do Contrato | Table | Engineering Contract Installment |  |  |
| amendments | Aditivos | Table | Engineering Contract Amendment |  |  |
| apply_amendment | Aplicar Aditivo | Button |  |  |  |
| observations | Observações | Text Editor |  |  |  |

### Office Expense

**Meta:** autoname=`format:OEXP-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| title | Título | Data |  |  |  |
| description | Descrição | Data |  | ✓ |  |
| expense_category | Categoria | Select | Aluguel Energia Água Internet Telefone Software/Assinatur... | ✓ |  |
| amount | Valor | Currency |  | ✓ |  |
| status | Status | Select | Pendente Pago Atrasado Cancelado |  |  |
| due_date | Data de Vencimento | Date |  |  |  |
| payment_date | Data de Pagamento | Date |  |  |  |
| payment_method | Forma de Pagamento | Select | PIX TED Boleto Dinheiro Cartão Débito Automático |  |  |
| is_recurring | Despesa Recorrente | Check |  |  |  |
| recurrence_frequency | Frequência | Select | Mensal Bimestral Trimestral Semestral Anual |  |  |
| next_due_date | Próximo Vencimento | Date |  |  |  |
| receipt | Comprovante | Attach |  |  |  |
| notes | Observações | Small Text |  |  |  |

### Payment

**Meta:** autoname=`format:PAY-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| title | Título | Data |  |  |  |
| project | Obra | Link | Construction Project | ✓ |  |
| customer | Cliente | Link | Customer | ✓ |  |
| origin_type | Origem | Select | Parcela do Contrato Despesa Reembolsável |  |  |
| contract | Contrato | Link | Engineering Contract |  |  |
| installment_number | Nº Parcela | Int |  |  |  |
| description | Descrição | Small Text |  |  |  |
| installment_origin_id | ID Origem | Data |  |  | ✓ |
| synced_at | Sincronizado em | Datetime |  |  |  |
| manual_override | Edição manual (não sincronizar) | Check |  |  |  |
| amount | Valor | Currency |  | ✓ |  |
| received_amount | Valor Recebido | Currency |  |  |  |
| due_date | Vencimento | Date |  |  |  |
| received_date | Data de Recebimento | Date |  |  |  |
| status | Status | Select | Pendente Vencido Recebido Cancelado Renegociado | ✓ |  |
| nf_number | Nº Nota Fiscal | Data |  |  |  |
| bank_account | Conta Bancária | Data |  |  |  |
| late_fee | Juros/Multa | Currency |  |  |  |
| notes | Observações | Small Text |  |  |  |
| receipt | Comprovante | Attach |  |  |  |

### Permit

**Meta:** autoname=`format:PROT-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| project | Obra | Link | Construction Project | ✓ |  |
| customer | Cliente | Link | Customer | ✓ |  |
| title | Título | Data |  |  |  |
| permit_type | Tipo de Alvará e Protocolo | Link | Permit Type | ✓ |  |
| permit_number | Número do Alvará ou Protocolo | Data |  |  |  |
| public_agency | Órgão Público | Link | Public Agency |  |  |
| status | Status | Select | Pendente Em análise Aprovado Indeferido Vencido Cancelado |  |  |
| protocol_date | Data do Alvará ou Protocolo | Date |  |  |  |
| expiry_date | Data de Validade | Date |  |  |  |
| document | Documento | Attach |  |  |  |
| art_rrt_number | Nº ART/RRT | Data |  |  |  |
| crea_cau_number | CREA/CAU do Responsável | Data |  |  |  |
| responsible_professional | Profissional Responsável | Data |  |  |  |
| art_validity_date | Validade | Date |  |  |  |
| art_fee | Taxa Paga | Currency |  |  |  |
| art_fee_receipt | Comprovante da Taxa | Attach |  |  |  |

### Project Document

**Meta:** autoname=`format:DOC-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| project | Obra | Link | Construction Project | ✓ |  |
| customer | Cliente | Link | Customer |  |  |
| category | Categoria | Link | Document Category | ✓ |  |
| status | Status | Select | Rascunho Assinado Protocolado Aprovado Vencido Substituído | ✓ |  |
| source | Origem | Select | Gerado pelo App Upload Manual Digitalizado |  |  |
| title_descriptor | Descritor | Data |  |  |  |
| title | Título | Data |  |  |  |
| version | Versão / Revisão | Data |  |  |  |
| file | Arquivo | Attach |  | ✓ |  |
| related_permit | Protocolo Relacionado | Link | Permit |  |  |
| remarks | Observações | Small Text |  |  |  |

### Project Item

**Meta:** autoname=`format:PITEM-{YYYY}-{#####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| form_help |  | HTML | <div class="form-message blue"><p><strong>Item do orçamen... |  |  |
| project | Obra | Link | Construction Project | ✓ |  |
| technical_item | Item do Catálogo Técnico | Link | Technical Item | ✓ |  |
| instance_label | Identificação | Data |  |  |  |
| stage | Etapa / Pavimento | Link | Project Stage |  |  |
| quantity | Quantidade | Int |  |  |  |
| unit | Unidade | Data |  |  |  |
| pricing_mode | Modo de precificação | Select | Fórmula Composição de custos |  |  |
| budget_revision | Revisão do orçamento | Int |  |  |  |
| bdi_percent | BDI % | Percent |  |  |  |
| direct_cost | Custo direto | Currency |  |  |  |
| total_value | Valor total (R$) | Currency |  |  |  |
| title | Título | Data |  |  |  |
| parameter_values | Parâmetros | Table | Project Item Parameter |  |  |
| unit_price | Preço unitário | Currency |  |  |  |
| cost_components | Componentes de custo | Table | Project Item Cost Component |  |  |
| computed_outputs | Resultados calculados | Table | Project Item Output |  |  |

### Reimbursable Expense

**Meta:** autoname=`format:REEMB-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| project | Obra | Link | Construction Project | ✓ |  |
| customer | Cliente | Link | Customer | ✓ |  |
| title | Título | Data |  |  |  |
| expense_category | Categoria | Link | Cost Category |  |  |
| supplier | Fornecedor | Link | Supplier |  |  |
| description | Descrição | Data |  | ✓ |  |
| payment | Recebimento | Link | Payment |  |  |
| amount | Valor Total | Currency |  | ✓ |  |
| total_office_paid | Total Pago pelo Escritório | Currency |  |  |  |
| office_outstanding | Saldo a Pagar (Escritório) | Currency |  |  |  |
| total_reimbursed | Total Reembolsado pelo Cliente | Currency |  |  |  |
| reimbursement_outstanding | Saldo a Reembolsar | Currency |  |  |  |
| await_client_reimbursement | Cliente deve reembolsar | Check |  |  |  |
| client_reimbursed_date | Data do último reembolso | Date |  |  |  |
| status | Status do Reembolso | Select | A reembolsar Parcialmente reembolsado Reembolsado Cancelado |  |  |
| office_payments | Pagamentos ao Fornecedor | Table | Reimbursable Expense Payment |  |  |
| reimbursements | Reembolsos Recebidos | Table | Reimbursable Expense Reimbursement |  |  |

### Subcontract

**Meta:** autoname=`format:SUBC-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| project | Obra | Link | Construction Project | ✓ |  |
| customer | Cliente | Link | Customer |  |  |
| supplier | Prestador | Link | Supplier | ✓ |  |
| funded_by | Quem arca | Select | Escritório Cliente | ✓ |  |
| cost_category | Categoria de Custo | Link | Cost Category |  |  |
| stage | Etapa | Link | Project Stage |  |  |
| description | Descrição do Serviço | Small Text |  |  |  |
| title | Título | Data |  |  |  |
| total_value | Valor Total | Currency |  | ✓ |  |
| total_paid | Total Pago | Currency |  |  |  |
| outstanding | Saldo a Pagar | Currency |  |  |  |
| amendment_remarks | Observações de Aditivo | Small Text |  |  |  |
| status | Status de Pagamento | Select | Open Partially Paid Paid Cancelled |  |  |
| payments | Pagamentos Efetuados | Table | Subcontract Payment |  |  |

### Task

**Meta:** autoname=`format:TSK-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`subject` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| project | Obra | Link | Construction Project |  |  |
| customer | Cliente | Link | Customer |  |  |
| stage | Etapa | Link | Project Stage |  |  |
| subject | Assunto | Data |  | ✓ |  |
| status | Status | Select | A fazer Fazendo Feito Cancelada |  |  |
| priority | Prioridade | Select | Baixa Média Alta |  |  |
| due_date | Prazo | Date |  |  |  |
| description | Descrição | Text Editor |  |  |  |
| assigned_to | Responsável | Link | User |  |  |
| completed_on | Concluída em | Date |  |  |  |

### Time Log

**Meta:** autoname=`format:TLOG-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| title | Título | Data |  |  |  |
| project | Obra | Link | Construction Project | ✓ |  |
| customer | Cliente | Link | Customer |  |  |
| log_date | Data | Date |  | ✓ |  |
| assigned_to | Responsável | Link | User |  |  |
| start_time | Hora Início | Time |  |  |  |
| end_time | Hora Fim | Time |  |  |  |
| duration_minutes | Duração (min) | Int |  |  |  |
| duration_hours | Duração (horas) | Float |  |  |  |
| activity | Atividade | Data |  | ✓ |  |
| category | Categoria | Select | Projeto Visita de Obra Reunião Deslocamento Projeto Técni... |  |  |
| details | Detalhes | Small Text |  |  |  |
| billable | Cobrável | Check |  |  |  |
| timer_display | Tempo Decorrido | HTML |  |  |  |
| timer_started_at | Início do Timer | Datetime |  |  |  |
| timer_active | Timer Ativo | Check |  |  |  |

### Work Cost

**Meta:** autoname=`format:WCST-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| project | Obra | Link | Construction Project | ✓ |  |
| customer | Cliente | Link | Customer |  |  |
| title | Título | Data |  |  |  |
| cost_category | Categoria de Custo | Link | Cost Category |  |  |
| supplier | Fornecedor | Link | Supplier |  |  |
| stage | Etapa | Link | Project Stage |  |  |
| description | Descrição | Data |  |  |  |
| nf_number | Nº Nota Fiscal | Data |  |  |  |
| cost_center | Centro de Custo | Data |  |  |  |
| date | Data do compromisso | Date |  |  |  |
| funded_by | Quem arca | Select | Escritório Cliente | ✓ |  |
| amount | Valor Total | Currency |  | ✓ |  |
| total_paid | Total Pago | Currency |  |  |  |
| outstanding | Saldo a Pagar | Currency |  |  |  |
| status | Status de Pagamento | Select | Open Partially Paid Paid Cancelled |  |  |
| payments | Pagamentos Efetuados | Table | Work Cost Payment |  |  |

#### Auxiliares (cadastro rígido)

### Cost Category

**Meta:** autoname=`field:category_name` · naming_rule=`By fieldname` · title_field=`category_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| category_name | Nome da Categoria | Data |  | ✓ | ✓ |

### Permit Type

**Meta:** autoname=`field:type_name` · naming_rule=`By fieldname` · title_field=`type_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| type_name | Nome do tipo | Data |  | ✓ | ✓ |
| is_art_rrt | ART/RRT | Check |  |  |  |

### Project Stage

**Meta:** autoname=`format:STGE-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| project | Obra | Link | Construction Project | ✓ |  |
| stage_type | Tipo de Etapa | Link | Stage Type | ✓ |  |
| status | Status | Select | Não iniciada Em andamento Concluída |  |  |
| progress | Avanço | Percent |  |  |  |
| weight | Peso relativo | Float |  |  |  |
| stage_value | Valor da etapa | Currency |  |  |  |
| order | Ordem | Int |  |  |  |
| title | Título | Data |  |  |  |
| start_date | Início | Date |  |  |  |
| expected_end | Previsão de Término | Date |  |  |  |
| actual_end | Término Real | Date |  |  |  |

### Project Stage Template

**Meta:** autoname=`field:template_name` · naming_rule=`By fieldname` · title_field=`template_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| template_name | Nome do Template | Data |  | ✓ | ✓ |
| project_type | Tipo de Projeto | Select | Execução Projeto Laudo Vistoria Consultoria Perícia Fisca... | ✓ |  |
| stages | Etapas | Table | Project Stage Template Item | ✓ |  |
| total_weight_display | Soma dos Pesos | HTML |  |  |  |

### Public Agency

**Meta:** autoname=`field:agency_name` · naming_rule=`By fieldname` · title_field=`agency_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| agency_name | Nome do Órgão | Data |  | ✓ | ✓ |
| sphere | Esfera | Select | Municipal Estadual Federal | ✓ |  |
| city | Cidade | Data |  |  |  |

### Stage Type

**Meta:** autoname=`field:stage_name` · naming_rule=`By fieldname` · title_field=`stage_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| stage_name | Nome da Etapa | Data |  | ✓ | ✓ |
| default_order | Ordem Padrão | Int |  |  |  |
| default_weight | Peso Padrão | Percent |  |  |  |

### Supplier

**Meta:** autoname=`field:supplier_name` · naming_rule=`By fieldname` · title_field=`supplier_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| supplier_name | Nome do Fornecedor | Data |  | ✓ | ✓ |
| cnpj | CNPJ | Data |  |  | ✓ |
| category | Categoria | Select | Material Serviço Mão de obra Outro |  |  |
| phone | Telefone | Data |  |  |  |
| email | E-mail | Data | Email |  |  |

### Technical Item

**Meta:** autoname=`field:item_name` · naming_rule=`By fieldname` · title_field=`item_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| item_name | Nome do Item | Data |  | ✓ | ✓ |
| item_key | Chave do Item | Data |  |  | ✓ |
| category | Categoria | Select | Estrutural Elétrica Hidráulica Acabamento Geral |  |  |
| data_type | Tipo de Dado (legado) | Select | Número Texto Sim-Não | ✓ |  |
| default_unit | Unidade Padrão (legado) | Data |  |  |  |
| fields | Campos | Table | Technical Item Field |  |  |
| outputs | Saídas | Table | Technical Item Output |  |  |

#### Child tables

### Commission Payment

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| payment_date | Data do Pagamento | Date |  | ✓ |  |
| amount | Valor | Currency |  | ✓ |  |
| reference | Referência | Data |  |  |  |
| receipt | Comprovante | Attach |  |  |  |
| remarks | Observações | Small Text |  |  |  |

### Construction Measurement Item

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| project_stage | Etapa | Link | Project Stage | ✓ |  |
| stage_description | Descrição da etapa | Data |  |  |  |
| previous_pct | % Anterior | Percent |  |  |  |
| current_pct | % Atual | Percent |  | ✓ |  |
| increment_pct | Incremento % | Percent |  |  |  |
| stage_value | Valor da etapa | Currency |  |  |  |
| measured_value | Valor medido | Currency |  |  |  |

### Customer Address

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| address_type | Tipo | Select | Residencial Comercial Correspondência Outro |  |  |
| cep | CEP | Data |  |  |  |
| street | Logradouro | Data |  | ✓ |  |
| number | Número | Data |  |  |  |
| complement | Complemento | Data |  |  |  |
| district | Bairro | Data |  |  |  |
| city | Cidade | Data |  |  |  |
| state | Estado | Select |  AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ... |  |  |
| is_primary | Endereço Principal | Check |  |  |  |

### Customer Contact

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| contact_name | Nome | Data |  | ✓ |  |
| contact_type | Tipo | Select | Principal Conjuge Responsável Outro |  |  |
| phone | Telefone | Data |  |  |  |
| mobile | Celular | Data |  |  |  |
| email | E-mail | Data | Email |  |  |
| notes | Observação | Small Text |  |  |  |

### Document Kit Item

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| document_template | Modelo de documento | Link | Document Template | ✓ |  |
| sort_order | Ordem | Int |  |  |  |

### Engineering Contract Amendment

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| amendment_date | Data | Date |  | ✓ |  |
| amendment_type | Tipo | Select | Adição Redução | ✓ |  |
| amount | Valor | Currency |  | ✓ |  |
| description | Descrição | Small Text |  |  |  |

### Engineering Contract Installment

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| payment_condition | Condição | Select | Data fixa Na conclusão Na aprovação A definir |  |  |
| due_date | Vencimento | Date |  |  |  |
| amount | Valor | Currency |  |  |  |
| received_amount | Valor Recebido | Currency |  |  |  |
| status | Status | Select | Pendente Vencido Recebido Cancelado |  |  |
| description | Descrição | Small Text |  |  |  |
| receipt_date | Data de Recebimento | Date |  |  |  |
| nf_number | Nº Nota Fiscal | Data |  |  |  |
| bank_account | Conta Bancária | Data |  |  |  |
| late_fee | Juros/Multa | Currency |  |  |  |
| installment_origin_id | ID de Origem | Data |  |  |  |
| payment | Recebimento | Link | Payment |  |  |

### Project Budget Revision

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| revision_number | Revisão | Int |  |  |  |
| revision_date | Data | Date |  |  |  |
| total_amount | Total | Currency |  |  |  |
| status | Status | Select | Rascunho Vigente Supersedida |  |  |
| notes | Observações | Small Text |  |  |  |

### Project Item Cost Component

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| description | Descrição do insumo | Data |  | ✓ |  |
| supplier | Fornecedor | Link | Supplier |  |  |
| quantity | Quantidade | Float |  |  |  |
| unit | Unidade | Data |  |  |  |
| unit_cost | Custo unitário | Currency |  |  |  |
| amount | Valor | Currency |  |  |  |

### Project Item Output

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| output_key | Chave | Data |  | ✓ |  |
| label | Resultado | Data |  |  |  |
| role | Papel | Data |  |  |  |
| value | Valor | Float |  |  |  |
| unit | Unidade | Data |  |  |  |

### Project Item Parameter

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| field_key | Chave | Data |  | ✓ |  |
| label | Campo | Data |  |  |  |
| value | Valor | Data |  |  |  |
| unit | Unidade | Data |  |  |  |
| data_type | Tipo de Dado | Data |  |  |  |
| required | Obrigatório | Check |  |  |  |

### Project Specification

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| technical_item | Modelo | Link | Technical Item | ✓ |  |
| instance_label | Identificação | Data |  |  |  |
| stage | Etapa / Pavimento | Link | Project Stage |  |  |
| field_key | Chave | Data |  | ✓ |  |
| label | Campo | Data |  |  |  |
| value | Valor | Data |  |  |  |
| unit | Unidade | Data |  |  |  |
| data_type | Tipo de Dado | Data |  |  |  |
| required | Obrigatório | Check |  |  |  |
| remarks | Observações | Small Text |  |  |  |

### Project Stage Template Item

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| stage_type | Tipo de Etapa | Link | Stage Type | ✓ |  |
| weight | Peso (%) | Percent |  | ✓ |  |
| sort_order | Ordem | Int |  |  |  |

### Reimbursable Expense Payment

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| payment_date | Data do Pagamento | Date |  | ✓ |  |
| amount | Valor | Currency |  | ✓ |  |
| payment_method | Forma de Pagamento | Select |  PIX TED Dinheiro Cartão Boleto Outro |  |  |
| reference | Referência | Data |  |  |  |
| receipt | Comprovante | Attach |  |  |  |
| remarks | Observações | Small Text |  |  |  |

### Reimbursable Expense Reimbursement

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| payment_date | Data do Recebimento | Date |  | ✓ |  |
| amount | Valor | Currency |  | ✓ |  |
| reference | Referência | Data |  |  |  |
| receipt | Comprovante | Attach |  |  |  |
| remarks | Observações | Small Text |  |  |  |

### Subcontract Payment

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| payment_date | Data do Pagamento | Date |  | ✓ |  |
| amount | Valor | Currency |  | ✓ |  |
| payment_method | Forma de Pagamento | Select |  PIX TED Dinheiro Cartão Boleto Outro |  |  |
| reference | Referência | Data |  |  |  |
| receipt | Comprovante | Attach |  |  |  |
| remarks | Observações | Small Text |  |  |  |

### Technical Item Field

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| field_key | Chave | Data |  | ✓ |  |
| label | Rótulo | Data |  | ✓ |  |
| unit | Unidade | Data |  |  |  |
| data_type | Tipo de Dado | Select | Número Texto Sim-Não | ✓ |  |
| default_value | Valor padrão | Data |  |  |  |
| required | Obrigatório | Check |  |  |  |
| sort_order | Ordem | Int |  |  |  |

### Technical Item Output

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| output_key | Chave | Data |  | ✓ |  |
| label | Rótulo | Data |  | ✓ |  |
| role | Papel do Resultado | Select |  value volume area preview |  |  |
| unit | Unidade | Data |  |  |  |
| formula | Fórmula | Small Text |  | ✓ |  |
| sort_order | Ordem | Int |  |  |  |

### Work Cost Payment

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| payment_date | Data do Pagamento | Date |  | ✓ |  |
| amount | Valor | Currency |  | ✓ |  |
| payment_method | Forma de Pagamento | Select |  PIX TED Dinheiro Cartão Boleto Outro |  |  |
| reference | Referência | Data |  |  |  |
| receipt | Comprovante | Attach |  |  |  |
| remarks | Observações | Small Text |  |  |  |

#### Single

### Engineering Settings

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=0 · issingle=1

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| company_name | Nome do Escritório | Data |  | ✓ |  |
| company_cnpj | CNPJ da Empresa | Data |  |  |  |
| company_crea | CREA da Empresa | Data |  |  |  |
| company_address_full | Endereço do Escritório | Small Text |  |  |  |
| company_logo | Logo do Escritório | Attach Image |  |  |  |
| engineer_full_name | Nome Completo | Data |  |  |  |
| engineer_cpf | CPF | Data |  |  |  |
| engineer_phone | Telefone | Data |  |  |  |
| engineer_email | E-mail | Data |  |  |  |
| default_notify_days | Dias padrão de antecedência (prazos) | Int |  |  |  |
| bank_name | Banco | Data |  |  |  |
| bank_agency | Agência | Data |  |  |  |
| bank_account | Conta | Data |  |  |  |
| bank_pix | Chave PIX | Data |  |  |  |

## 5. hooks.py (resumo)

### fixtures
- Workspace `Engenharia`, Notification (4), Print Format (15), Custom Field Event `custom_source%`, Role (2), Kanban Board

### app_include_css
- `/assets/engenharia/css/list_filters.css`
- `/assets/engenharia/css/reports.css`
- `/assets/engenharia/css/hub.css`
- `/assets/engenharia/css/dashboard.css`
- `/assets/engenharia/css/sidebar_fix.css`

### app_include_js
- `/assets/engenharia/js/masks.js`
- `/assets/engenharia/js/list_nav.js`
- `/assets/engenharia/js/list_filters.js`
- `/assets/engenharia/js/customer_from_project.js`
- `/assets/engenharia/js/documents_placeholders.js`
- `/assets/engenharia/js/timer_global.js`
- `/assets/engenharia/js/reports_common.js`
- `/assets/engenharia/js/hub.js`

### boot_session
- `engenharia.boot.boot_session` → `bootinfo.eng_office` (logo, dados do escritório para print)

### scheduler_events
- **daily:** check_overdue_installments, check_overdue_office_expenses, check_overdue_reimbursable_expenses, notify_deadlines_daily, notify_expiring_permits, notify_overdue_tasks, notify_overdue_payments
- **weekly:** check_project_status_weekly

### doc_events
- Engineering Contract, Reimbursable Expense, Engineering Contract Installment, Payment, Deadline, Permit, Project Stage

### after_migrate
reinstall_child_doctypes → roles → ensure_event_custom_fields → permissions → seed → translations → sidebar → reports → print_formats → workspace

## 6. API whitelisted (facade e principais)

| Função | Módulo | Permissão |
| --- | --- | --- |
| get_dashboard_data | dashboard_api | Construction Project read |
| mark_payment_received | dashboard_api | Payment write |
| mark_office_expense_paid | dashboard_api | Office Expense write |
| get_consolidated_costs | engenharia.api.costs | Construction Project read |
| get_project_hub_data | project_hub | Construction Project read |
| get_active_projects / get_project_summary | agent_api | Construction Project read |
| get_placeholder_reference | documents | Document Template read |
| bulk_delete_payments / resync / cancel | financial | Payment / Contract write |
| create_next_office_expense | office_expense | Office Expense create |
| apply_template_to_project | stage_template | Construction Project write |

## 7. Testes

- **344** métodos em **61** arquivos.
- `bench --site engenharia.local run-tests --app engenharia`

