# Seção 2 — Cross-check de Links entre DocTypes

**App:** `engenharia` · **Data:** 2026-06-06 (revisão 2026-06-09)

> **Adições:** `Office Expense` (standalone, sem `project`), `Project Stage Template`, sidebar em `workspace_sidebar/engenharia.json` (~37 itens).

---

## 2.1 Mapa de relacionamentos

```
Customer
  ├── contacts (Table → Customer Contact)
  ├── addresses (Table → Customer Address)
  └── Linkado POR:
      ├── Construction Project.customer
      ├── Engineering Contract.customer
      └── (fetch_from indireto via project em satélites)

Construction Project  [HUB]
  ├── customer (Link → Customer)
  ├── budget_revisions (Table → Project Budget Revision)
  └── Linkado POR:
      ├── Engineering Contract.project
      ├── Payment.project
      ├── Work Cost.project
      ├── Subcontract.project
      ├── Reimbursable Expense.project
      ├── Commission.construction_project
      ├── Deadline.project
      ├── Permit.project
      ├── Task.project
      ├── Communication Log.project
      ├── Time Log.project
      ├── Project Stage.project
      ├── Project Item.project
      └── Construction Measurement.project

Office Expense  [standalone — custos escritório, sem project]
  └── integra: cash_flow (saídas), dashboard Manager (pendentes)

Project Stage Template  [cadastro]
  └── aplicado em Construction Project via stage_template.py

Engineering Contract
  ├── project, customer (Link)
  ├── installments (Table → Engineering Contract Installment)
  │     └── installment.payment → Payment
  ├── amendments (Table → Engineering Contract Amendment)
  └── Linkado POR: Payment.contract

Commission
  ├── construction_project (Link → Construction Project)
  ├── payments (Table → Commission Payment)
  └── Linkado POR: Construction Project links (Financeiro)

Project Item
  ├── project, technical_item, stage (Link)
  ├── parameter_values (Table → Project Item Parameter)
  ├── cost_components (Table → Project Item Cost Component)
  ├── computed_outputs (Table → Project Item Output)
  └── Rollup → Construction Project.spec_project_total

Technical Item
  ├── fields (Table → Technical Item Field)
  ├── outputs (Table → Technical Item Output)
  └── Linkado POR: Project Item.technical_item, Project Specification (legado)

Work Cost
  ├── project, customer, cost_category, supplier, stage (Link)
  └── Sem filhos

Subcontract
  ├── project, customer, supplier (Link)
  ├── payments (Table → Subcontract Payment)
  └── `funded_by` Escritório/Cliente — caixa do escritório via `office_subcontract_filters()`

Payment
  ├── project, customer, contract (Link)
  └── Sync ← Engineering Contract Installment

Deadline / Permit / Task / Time Log / Communication Log
  └── project (+ customer fetch_from project)

Construction Measurement
  ├── project, customer
  └── items (Table → Construction Measurement Item) → project_stage

Document Kit
  └── templates (Table → Document Kit Item) → document_template

Cadastros (leaf): Supplier, Cost Category, Stage Type, Permit Type, Public Agency, Document Template
Engineering Settings: Single (sem links)
Project Specification: child legado (istable, deprecated)
```

---

## 2.2 Integridade dos campos Link

| DocType | Fieldname | Target | fetch_from | set_query JS | Observação |
|---|---|---|---|---|---|
| Commission | construction_project | Construction Project | — | ✅ Sim (exclui Cancelada) | OK |
| Engineering Contract | project | Construction Project | customer ← project.customer | ❌ | 🟡 Sem filtro status |
| Payment | project | Construction Project | customer ← project.customer | ❌ | OK |
| Work Cost | project | Construction Project | customer ← project.customer; `funded_by` Escritório/Cliente | ❌ | OK |
| Subcontract | project | Construction Project | customer ← project.customer; `funded_by` Escritório/Cliente | ❌ | OK |
| Subcontract | supplier | Supplier | — | ❌ | OK |
| Task | project | Construction Project | customer ← project.customer | ❌ | OK |
| Project Item | technical_item | Technical Item | unit ← technical_item.default_unit | ❌ | OK |
| Project Item | stage | Project Stage | — | ❌ | 🟡 Poderia filtrar por project |
| Permit | permit_type | Permit Type | — | ❌ | OK |
| Permit | public_agency | Public Agency | — | ❌ | OK |
| Reimbursable Expense | expense_category | Cost Category | — | ❌ | OK |
| Document Kit Item | document_template | Document Template | — | ❌ | OK |
| Measurement Item | project_stage | Project Stage | stage_value ← project_stage.stage_value | ❌ | OK |

**fetch_from — validação:**

| fetch_from | Campo source existe? | Compatível? |
|---|---|---|
| `project.customer` | ✅ Customer link no projeto | ✅ |
| `technical_item.default_unit` | ✅ Data no Technical Item | ✅ |
| `project_stage.stage_value` | ⚠️ Verificar se field `stage_value` existe em Project Stage | 🟡 Confirmar nome do campo (pode ser `progress_percent` ou custom) |

---

## 2.3 Connections e Sidebar

### `links` no JSON (aba Conexões)

| DocType | Tem links? | Grupos |
|---|---|---|
| **Construction Project** | ✅ 12 links | Financeiro (5), Agenda (3), Comunicação, Produtividade, Administração, Especificações |
| **Customer** | ✅ 2 links | Obras, Financeiro |
| **Demais 22 standalone** | ❌ vazio | — |

### `internal_links` (dashboard DocType)

| Arquivo | internal_links |
|---|---|
| `commission/commission_dashboard.py` | `Construction Project` ← `construction_project` |

### Gaps de connections

| Problema | Severidade | Sugestão |
|---|---|---|
| Engineering Contract sem links de volta para Payment/Work Cost | 🟡 | Adicionar `links` no JSON do contrato |
| Commission sem links para Payment (não aplicável — fluxo próprio) | 🟢 | OK |
| Customer não linka Commission, Deadline, Task | 🟡 | Opcional — hub é Construction Project |
| DocTypes financeiros sem `links` | 🟡 | Manager vê via workspace/sidebar |

### Sidebar / Workspace

Links operacionais via `setup/sidebar.py` + fixture Workspace **Engenharia**. Engenharia User **não vê** atalhos financeiros (permissoes DocType) — sidebar oculta por permissão nativa Frappe.

**Órfãos:** Nenhum link aponta para DocType inexistente. `Project Specification` existe mas está deprecated (patch migra para Project Item).

---

## 2.4 fetch_from — lista completa

1. `Task.customer` ← `project.customer`
2. `Permit.customer` ← `project.customer`
3. `Reimbursable Expense.customer` ← `project.customer`
4. `Payment.customer` ← `project.customer`
5. `Communication Log.customer` ← `project.customer`
6. `Time Log.customer` ← `project.customer`
7. `Engineering Contract.customer` ← `project.customer`
8. `Deadline.customer` ← `project.customer`
9. `Construction Measurement.customer` ← `project.customer` (fetch_if_empty)
10. `Work Cost.customer` ← `project.customer` (fetch_if_empty)
11. `Project Item.unit` ← `technical_item.default_unit`
12. `Construction Measurement Item.stage_value` ← `project_stage.stage_value`

---

*Auditoria somente leitura.*
