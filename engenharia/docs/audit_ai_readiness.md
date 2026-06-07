# Seção 7 — Preparação para IA (Futuro)

**App:** `engenharia` · **Data:** 2026-06-06

---

## 7.1 Superfície de API — `@frappe.whitelist()`

| Função | Módulo | Parâmetros | Permission check | Descrição |
|---|---|---|---|---|
| `get_dashboard_data` | dashboard_api.py | limit, period_days, list_limits | ✅ Construction Project read | Payload painel |
| `mark_payment_received` | dashboard_api.py | payment_name, received_date | ✅ Delegado Payment write | Marca recebido |
| `get_active_projects` | agent_api.py | — | ✅ Construction Project read | Lista obras ativas |
| `get_project_summary` | agent_api.py | project | ✅ Construction Project read | Resumo + financeiro agregado |
| `get_costs_by_category` | agent_api.py | project | ✅ Project read + Work Cost read | Custos por categoria |
| `resync_contract_payments` | financial.py | contract_name | ✅ Contract write | Re-sync parcelas |
| `bulk_delete_payments` | financial.py | names | ✅ Payment delete | Exclusão massa |
| `cancel_contract_payment` | financial.py | payment_name | 🟡 Payment write (sem throw) | Cancela pagamento |
| `get_construction_project_spec_preview` | project_rollup.py | project | ✅ Project read | HTML preview specs |
| `generate_project_documents` | documents.py | project_name, template_names | ✅ Project write | Gera docx em lote |
| `get_available_templates` | documents.py | — | ✅ Document Template read | Lista templates |
| `get_available_kits` | documents.py | — | ✅ Document Kit read | Lista kits |
| `get_placeholder_reference` | documents.py | — | ✅ Document Template read | Catálogo de placeholders |
| `apply_contract_amendment` | engineering_contract.py | contract, ... | ✅ Contract write | Aplica aditivo |
| `start_timer` / `stop_timer` | time_log.py | — | ✅ Time Log | Timer |
| `get_active_user_timer` | time_log.py | — | ✅ | Timer ativo |
| `add_project_item_from_template` | project_item.py | — | ✅ | Cria item |
| `get_specifications_preview` | construction_project.py | project | ✅ | Preview specs |
| `import_csv` | construction_project.py | — | ✅ | Import CSV |
| `create_deadline_from_template` | deadline.py | — | ✅ | Atalho prazo |

---

## 7.2 Completude REST API (`/api/resource/`)

DocTypes `custom: 0` expõem CRUD REST automaticamente com permissões DocPerm.

| Aspecto | Status |
|---|---|
| CRUD Construction Project | ✅ User: RW sem delete; Manager: full |
| CRUD Commission/Payment/Contract | ✅ Manager only |
| Título auto-composto | ✅ API create → validate preenche title |
| Campos read_only | ✅ Respeitados |
| Child tables via API | ✅ Nested save no parent |

**Gap:** 🟡 Engenharia User recebe 403 em financeiros — agente precisa credencial Manager ou endpoints filtrados.

---

## 7.3 Gaps para agente IA (MCP / Hermes)

| Operação | Possível hoje? | Gap |
|---|---|---|
| Criar projeto novo | ✅ REST POST | Fornecer customer name/id |
| Listar projetos ativos | ✅ `agent_api.get_active_projects` | — |
| Criar deadline com alerta | ✅ REST POST Deadline | Notificação é async scheduler |
| Consultar comissões pendentes | 🟡 Manager REST / QB | User role bloqueado |
| Registrar pagamento comissão | 🟡 REST PATCH Commission child | Sem whitelist dedicado |
| Gerar documento template | ✅ `documents.generate_project_documents` | — |
| Consultar KPIs dashboard | ✅ `get_dashboard_data` | User sem financeiro |
| Prazos vencendo semana | 🟡 REST GET Deadline filters | Sem whitelist dedicado |
| Criar medição | ✅ REST POST | — |
| Consultar saldo contrato | 🟡 `get_project_summary` | Expõe financeiro — role issue |
| Registrar Work Cost | ✅ Manager REST (`funded_by` Escritório/Cliente) | User bloqueado |
| Registrar Subcontract | ✅ Manager REST (`funded_by` Escritório/Cliente) | User bloqueado |
| Timer Time Log | ✅ whitelisted | — |

---

## 7.4 Recomendações IA-readiness

### Endpoints sugeridos (não existem)

1. 🟡 `get_pending_commissions(project=None)` — Manager  
2. 🟡 `get_deadlines_due(days=7, project=None)` — ambos roles  
3. 🟡 `get_project_financial_summary` — **separar** versão User (sem valores) vs Manager  

### Schema / DX

| Item | Ação |
|---|---|
| Field `description` em campos ambíguos (Project Item outputs) | 🟡 |
| Mensagens `frappe.throw` descritivas | 🟢 em geral OK |
| API Key auth | ✅ Frappe nativo |
| Role Engenharia User vs Manager | 🔴 Agente financeiro **deve** usar Manager ou endpoints novos |

### Segurança IA

| Risco | Severidade |
|---|---|
| `get_project_summary` vaza financeiro para User com read projeto | 🟡 |
| `agent_api` não verifica role Manager antes de totais | 🟡 |
| Dashboard redaction | ✅ OK |

---

*Auditoria somente leitura.*
