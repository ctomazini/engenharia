# Seção 7 — Preparação para IA

**App:** `engenharia` · **Status:** Fase 1 implementada · **Data:** 2026-06-07 · **Versão:** 1.0.0

---

## 7.1 Estado atual

| Componente | Status |
|---|---|
| `agent_api.py` | ✅ Implementado (4 endpoints) |
| `test_agent_api.py` | ✅ 9 testes |
| Endpoints agregados para agente | ✅ Read-only |
| Documentação de contrato IA | ✅ Este arquivo + `engenharia/docs/README.md` |
| REST `/api/resource/` em DocTypes | ✅ Nativo Frappe (40 DocTypes `custom: 0`) |
| Permissões role-aware | ✅ `setup/permissions.py` + redação financeira no summary |

O app está **operacional para humanos** e **pronto para integração MCP/Hermes** via endpoints agregados. Fase 2 (tools MCP registradas) permanece no backlog.

**Gap vs advocacia:** paridade Fase 1 fechada (incl. `get_financial_overview`). Contadores em `get_active_projects` permanecem backlog opcional.

---

## 7.2 Superfície existente

### `agent_api.py` (Fase 1 — implementado)

| Função | Permission | Retorno |
|---|---|---|
| `get_active_projects` | Construction Project read | Obras ativas + `customer_name` (batch lookup) |
| `get_project_summary` | Construction Project read | Prazos; financeiro condicional (Manager) |
| `get_costs_by_category` | Manager + Work Cost read | Custos agregados por Cost Category |
| `get_financial_overview` | Manager + Payment read | Inadimplência e recebimentos do mês |

**Regras aplicadas:** read-only · `has_permission(..., throw=True)` · type hints · zero `commit()` · financeiro omitido para Engenharia User (espelha dashboard).

### Whitelists complementares (candidatos a tools MCP)

| Função | Módulo | Permission | Uso por agente |
|---|---|---|---|
| `get_dashboard_data` | dashboard_api.py | Construction Project read | Snapshot operacional do escritório |
| `construction_project_query` | construction_project.py | Construction Project read | Autocomplete obras |
| `generate_project_documents` | documents.py | Construction Project write | Gerar docx |
| `get_placeholder_reference` | documents.py | Document Template read | Referência de placeholders |
| `get_active_user_timer` | time_log.py | Time Log read | Timer ativo |
| `get_project_items_summary` | project_rollup.py | Construction Project read | Orçamento / itens técnicos |

---

## 7.3 Equivalência engenharia ↔ advocacia

| Engenharia | Advocacia | Paridade |
|---|---|---|
| `get_active_projects` | `get_active_cases` | 🟡 Eng. sem contadores de satélites na lista; advocacia usa 3× `db.count` por caso |
| `get_project_summary` | `get_case_summary` | 🟡 Eng. omite financeiro para User; advocacia retorna `financial_restricted: true` |
| `get_costs_by_category` | `get_court_costs_by_type` | ✅ Agregação por tipo/categoria, Manager only |
| `get_financial_overview` | `get_financial_overview` | ✅ Inadimplência/recebimentos do mês (escritório) |

---

## 7.4 Payload exemplo — `get_project_summary`

```json
{
  "project": "PROJ-2026-0042",
  "title": "PROJ-2026-0042 — Construtora Exemplo Ltda",
  "customer": "CLI-2026-0015",
  "customer_name": "Construtora Exemplo Ltda",
  "status": "Em andamento",
  "upcoming_deadlines": [],
  "contract_value": 150000.0,
  "amount_receivable": 12000.0,
  "pending_payments_count": 2,
  "total_costs": 45000.0,
  "margin": 105000.0
}
```

Para **Engenharia User**, chaves em `_FINANCIAL_SUMMARY_KEYS` são omitidas e `financial_restricted: true` é retornado.

---

## 7.5 Testes (`test_agent_api.py`)

| Teste | Assert |
|---|---|
| `test_get_active_projects` | Lista + `customer_name` |
| `test_get_project_summary` | KPIs financeiros (Administrator/Manager) |
| `test_get_project_summary_redacts_financial_for_user` | Sem valores para User |
| `test_get_costs_by_category` | Agregação por categoria |
| `test_get_costs_by_category_requires_manager` | PermissionError para User |
| `test_get_financial_overview_returns_dict` | Contadores operacionais |
| `test_get_financial_overview_has_amounts` | Totais monetários |
| `test_get_financial_overview_requires_manager` | PermissionError para User |
| `test_permission_denied_without_access` | PermissionError sem role |

---

## 7.6 Roadmap restante

### Fase 1.5 — Paridade advocacia

1. ~~`get_financial_overview()` + testes.~~ ✅
2. ~~`financial_restricted: true` no summary para User.~~ ✅
3. Opcional: contadores leves em `get_active_projects` (deadlines/payments pendentes) com batch query — **sem** N+1.

### Fase 2 — Tools MCP

1. Registrar tools espelhando `agent_api.py`.
2. OpenAPI ou docstring estruturada exportável.
3. Smoke com Cursor MCP ou script `xcall`.

---

*Auditoria somente leitura — atualizada na release v1.0.0.*
