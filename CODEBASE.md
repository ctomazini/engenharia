# CODEBASE — App Engenharia (Frappe v16)

> Gerado em **2026-06-07** — inventário técnico do app greenfield EN. Frappe puro, **sem ERPNext**.

> **HEAD:** `8c907d2 2026-06-07 18:00:02 +0000 docs: complete document placeholders and sync all documentation`

---

## 1. Visão Geral

| Item | Valor |
| --- | --- |
| Nome | engenharia |
| Framework | Frappe v16 |
| Licença | MIT |
| Site dev | engenharia.local |
| Linhas Python | ~15113 |
| Linhas JavaScript | ~3781 |
| Métodos de teste | 239 |
| DocTypes | 40 (`custom: 0`) |
| Script Reports | 5 |

**Propósito:** gestão de obras — projetos, contratos, custos, subcontratos, prazos, protocolos, pagamentos, painel modular, documentos `.docx`.

**Deps:** `docxtpl>=0.18.0`.

**Commits recentes:**
```text
8c907d2 docs: complete document placeholders and sync all documentation
3cc6f0a feat(reports): add charts, KPIs and color formatting to script reports
eba1b47 docs: add deploy-ready audit report (2026-06-07)
0cf9a54 fix: add type hints to whitelisted APIs and justify ignore_permissions
8adb0ae docs: organize documentation index and E2E guide
3c6be43 test(e2e): add Playwright session covering full app flow
46527f4 feat(communication-log): add standard filters for date and type
de7d40d feat(time-log): add standard filters for project and date
6419739 feat(list-filters): add responsive standard filter bar
a0959c0 fix(dashboard): stabilize partial refresh layout
ee5f01b fix(dashboard): refresh period filter without full page reload
b349346 style(dashboard): restore horizontal quick-actions carousel on mobile
```

## 2. Árvore de Arquivos (anotada)

```text
engenharia/
├── CODEBASE.md, README.md, REGRAS_OBRIGATORIAS.md, pyproject.toml
└── engenharia/
    ├── hooks.py, dashboard_api.py, documents.py, financial.py, notifications.py
    ├── public/js/ (masks, list_nav, customer_from_project, documents_placeholders, dashboard/*)
    ├── setup/ (install, sidebar, workspace, reports, reinstall_child_doctypes)
    └── engenharia/ (doctype/, report/, page/eng_dashboard/)
```

## 3. Mapa de DocTypes

#### Standalone / transacionais

### Commission

**Meta:** autoname=`format:CMSN-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| construction_project | Projeto | Link | Construction Project | ✓ |  |
| commission_type | Tipo de Comissão | Select | Pré-Moldado Outro | ✓ |  |
| supplier_name | Fornecedor | Data |  | ✓ |  |
| supplier_tax_id | CNPJ do Fornecedor | Data |  |  |  |
| description | Descrição | Small Text |  |  |  |
| title | Título | Data |  |  |  |
| total_value | Valor Total | Currency |  | ✓ |  |
| total_paid | Total Pago | Currency |  |  |  |
| outstanding | Saldo a Receber | Currency |  |  |  |
| status | Status | Select | Open Partially Paid Paid Cancelled |  |  |
| payments | Pagamentos Recebidos | Table | Commission Payment |  |  |

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
| next_steps | Próximos Passos | Small Text |  |  |  |
| create_task | Gerar Tarefa | Check |  |  |  |
| task | Tarefa Gerada | Link | Task |  |  |

### Construction Measurement

**Meta:** autoname=`format:MED-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
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
| construction_area | Área Construída (m²) | Float |  |  |  |
| current_contract_value | Valor Atual do Contrato | Currency |  |  |  |
| commission_outstanding | Comissões a Receber | Currency |  |  |  |
| commission_summary_panel | Resumo de comissões | HTML | <p class="text-muted">Carregando comissões...</p> |  |  |
| physical_progress | Avanço Físico Global | Percent |  |  |  |
| responsible_engineer | Responsável Técnico | Data |  |  |  |
| crea_number | CREA do Responsável | Data |  |  |  |
| art_number | Nº ART Principal | Data |  |  |  |
| property_registration | Matrícula do Imóvel | Data |  |  |  |
| gps_coordinates | Coordenadas GPS | Data |  |  |  |
| budget_revision | Revisão vigente | Int |  |  |  |
| default_bdi_percent | BDI padrão % | Percent |  |  |  |
| budget_revisions | Revisões de orçamento | Table | Project Budget Revision |  |  |
| specs_help | Itens técnicos | HTML | <p class="text-muted">Use <b>Adicionar especificação</b>,... |  |  |
| spec_preview_panel | Prévia das especificações | HTML | <p class="text-muted">Carregando prévia...</p> |  |  |
| spec_items_summary_panel | Especificações da Obra | HTML | <p class="text-muted">Carregando especificações...</p> |  |  |
| spec_project_total | Total especificações (obra) | Currency |  |  |  |
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
| cnpj | CNPJ | Data |  |  | ✓ |
| nationality | Nacionalidade | Data |  |  |  |
| marital_status | Estado Civil | Select |  Solteiro(a) Casado(a) Divorciado(a) Viúvo(a) União Estável |  |  |
| profession | Profissão | Data |  |  |  |
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
| template_name | Nome do Template | Data |  | ✓ | ✓ |
| document_type | Tipo | Select | Contrato Proposta Relatório Outro |  |  |
| description | Descrição | Small Text |  |  |  |
| document_file | Arquivo .docx | Attach |  | ✓ |  |
| enabled | Habilitado | Check |  |  |  |
| view_placeholders | Ver Placeholders Disponíveis | Button |  |  |  |

### Engineering Contract

**Meta:** autoname=`format:CNTR-{YYYY}-{####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| project | Obra | Link | Construction Project | ✓ |  |
| customer | Cliente | Link | Customer | ✓ |  |
| title | Título | Data |  |  |  |
| status | Status | Select | Vigente Encerrado Cancelado Quitado |  |  |
| base_value | Valor Base | Currency |  | ✓ |  |
| current_value | Valor Atual | Currency |  |  |  |
| adjustment_index | Índice de Reajuste | Select |  INCC IPCA IGP-M Nenhum |  |  |
| technical_retention_pct | Retenção Técnica % | Percent |  |  |  |
| late_fee_pct | Multa Mora % | Percent |  |  |  |
| daily_interest_pct | Juros Diários % | Float |  |  |  |
| installment_count | Número de Parcelas | Int |  |  |  |
| first_installment_date | Data da Primeira Parcela | Date |  |  |  |
| installment_value | Valor da Parcela | Currency |  |  |  |
| generate_installments | Gerar Parcelas | Button |  |  |  |
| installments | Parcelas | Table | Engineering Contract Installment |  |  |
| amendments | Aditivos | Table | Engineering Contract Amendment |  |  |
| apply_amendment | Aplicar Aditivo | Button |  |  |  |
| observations | Observações | Text Editor |  |  |  |

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
| due_date | Vencimento | Date |  | ✓ |  |
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
| permit_type | Tipo de Protocolo | Link | Permit Type | ✓ |  |
| permit_number | Número do Protocolo | Data |  |  |  |
| public_agency | Órgão Público | Link | Public Agency |  |  |
| status | Status | Select | Pendente Em análise Aprovado Indeferido Vencido Cancelado |  |  |
| protocol_date | Data do Protocolo | Date |  |  |  |
| expiry_date | Data de Validade | Date |  |  |  |
| document | Documento | Attach |  |  |  |
| art_rrt_number | Nº ART/RRT | Data |  |  |  |
| crea_cau_number | CREA/CAU do Responsável | Data |  |  |  |
| responsible_professional | Profissional Responsável | Data |  |  |  |
| art_validity_date | Validade | Date |  |  |  |
| art_fee | Taxa Paga | Currency |  |  |  |
| art_fee_receipt | Comprovante da Taxa | Attach |  |  |  |

### Project Item

**Meta:** autoname=`format:PITEM-{YYYY}-{#####}` · naming_rule=`Expression (old style)` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| project | Obra | Link | Construction Project | ✓ |  |
| technical_item | Item Técnico | Link | Technical Item | ✓ |  |
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
| status | Status | Select | A reembolsar Reembolsado Cancelado |  |  |
| payment | Pagamento | Link | Payment |  |  |
| amount | Valor | Currency |  | ✓ |  |
| payment_date | Data do pagamento pelo escritório | Date |  |  |  |
| await_client_reimbursement | Cliente deve reembolsar | Check |  |  |  |
| client_reimbursed_date | Data do recebimento do cliente | Date |  |  |  |
| receipt | Comprovante | Attach |  |  |  |

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
| status | Status | Select | Open Partially Paid Paid Cancelled |  |  |
| amendment_remarks | Observações de Aditivo | Small Text |  |  |  |
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
| amount | Valor | Currency |  | ✓ |  |
| date | Data | Date |  |  |  |
| funded_by | Quem arca | Select | Escritório Cliente | ✓ |  |
| payment_method | Forma de Pagamento | Select |  PIX TED Dinheiro Cartão Boleto Outro |  |  |
| status | Status | Select | Pago Pendente Cancelado |  |  |
| receipt | Comprovante | Attach |  |  |  |

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
| due_date | Vencimento | Date |  | ✓ |  |
| amount | Valor | Currency |  |  |  |
| received_amount | Valor Recebido | Currency |  |  |  |
| status | Status | Select | Pendente Vencido Recebido Cancelado |  |  |
| description | Descrição | Small Text |  |  |  |
| receipt_date | Data de Recebimento | Date |  |  |  |
| nf_number | Nº Nota Fiscal | Data |  |  |  |
| bank_account | Conta Bancária | Data |  |  |  |
| late_fee | Juros/Multa | Currency |  |  |  |
| installment_origin_id | ID de Origem | Data |  |  |  |
| payment | Pagamento | Link | Payment |  |  |

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

#### Single

### Engineering Settings

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=0 · issingle=1

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| company_name | Nome do Escritório | Data |  | ✓ |  |
| company_cnpj | CNPJ da Empresa | Data |  |  |  |
| company_crea | CREA da Empresa | Data |  |  |  |
| company_logo | Logo do Escritório | Attach Image |  |  |  |
| default_notify_days | Dias padrão de antecedência (prazos) | Int |  |  |  |
| bank_name | Banco | Data |  |  |  |
| bank_agency | Agência | Data |  |  |  |
| bank_account | Conta | Data |  |  |  |
| bank_pix | Chave PIX | Data |  |  |  |

## 4. hooks.py (resumo)

### app_include_js
- `/assets/engenharia/js/masks.js`
- `/assets/engenharia/js/list_nav.js`
- `/assets/engenharia/js/list_filters.js`
- `/assets/engenharia/js/customer_from_project.js`
- `/assets/engenharia/js/documents_placeholders.js`
- `/assets/engenharia/js/timer_global.js`

### scheduler_events
- **daily:** check_overdue_installments, check_overdue_reimbursable_expenses, notify_deadlines_daily, notify_expiring_permits, notify_overdue_tasks, notify_overdue_payments
- **weekly:** check_project_status_weekly

### after_migrate
reinstall_child_doctypes → roles → permissions → seed → translations → sidebar → reports → workspace

## 5. API whitelisted (facade)

| Função | Módulo | Permissão |
| --- | --- | --- |
| get_dashboard_data | dashboard_api | Construction Project read |
| mark_payment_received | dashboard_api | Payment write |
| construction_project_query | construction_project | Construction Project read |
| get_placeholder_reference | documents | Document Template read |
| bulk_delete_payments / resync / cancel | financial | Payment / Contract write |

## 6. Testes

- **239** métodos em **48** arquivos.
- `bench --site engenharia.local run-tests --app engenharia`

