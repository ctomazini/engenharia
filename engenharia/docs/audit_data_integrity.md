# Seção 5 — Integridade de Dados e Rollups

**App:** `engenharia` · **Data:** 2026-06-06 (nota 2026-06-09: Office Expense no fluxo de caixa; ver `test_report_cash_flow`)

---

## 5.1 Rollups financeiros e agregados

### Cadeia Project Item → Construction Project

```
Technical Item (outputs/fórmulas)
  → Project Item.total_value (output role "value")
    → Construction Project.spec_project_total (sum items da revisão vigente)
    → Project Budget Revision.total_amount (linha Vigente)
```

| Evento | Recalcula? | Mecanismo |
|---|---|---|
| Project Item insert/update/trash | ✅ | `on_project_item_change()` → `recompute_construction_project_specs()` |
| Teste paridade sum(items)==spec_project_total | ✅ | `test_rollup.py`, `test_project_budget.py` |
| Delete Project Item | ✅ | Hook `on_trash` chama rollup |

**Severidade:** 🟢 OK

---

### Commission → Construction Project

```
Commission.payments (child)
  → total_paid = Σ amount
  → outstanding = total_value - total_paid
  → Construction Project.commission_outstanding = Σ outstanding (status != Cancelled)
```

| Evento | Recalcula? | Mecanismo |
|---|---|---|
| Commission validate (payments change) | ✅ | `compute_totals()`, `update_status()` |
| Commission on_update / on_trash | ✅ | `sync_project_commission_outstanding()` via frappe.qb |
| Delete Commission | ✅ | on_trash sync exclui registro |
| Teste | ✅ | `test_sync_project_commission_outstanding` |

**Severidade:** 🟢 OK

---

### Engineering Contract → Payment

| Aspecto | Status |
|---|---|
| Installments child com `installment_origin_id` | ✅ |
| Sync idempotente on_update contrato | ✅ `financial.sync_payments_from_contract` |
| Flag reentrância `frappe.flags.in_payment_sync` | ✅ |
| Aditivos recalculam `current_value` | ✅ controller |
| Testes sync | ✅ `test_financial.py`, `test_engineering_contract.py` |

**Severidade:** 🟢 OK

---

### Work Cost / Reimbursable Expense / Payment

| DocType | Rollup | Teste |
|---|---|---|
| Work Cost | Totais por categoria via `work_costs.py`; `funded_by` separa caixa do escritório vs registro do cliente | test_work_cost |
| Reimbursable Expense | Sync Payment filho | test_reimbursable_expense |
| Payment | Status Vencido/Pendente/Recebido | test_payment, scheduler |

**Work Cost / Subcontract `funded_by`:** `Escritório` entra em KPIs, fluxo de caixa, composição do painel e margem realizada; `Cliente` permanece na obra e relatórios analíticos, mas é excluído do caixa do escritório via `office_cash_flow_filters()` / `office_subcontract_filters()` em `work_costs.py`. Saídas do mês somam Work Cost + pagamentos de subcontrato do escritório (`get_firm_month_outflows`).

---

## 5.2 Validações de consistência

| Regra | Onde | Status |
|---|---|---|
| Valores negativos bloqueados | Commission `total_value > 0`; Work Cost amount | ✅ |
| Overpayment Commission | ✅ throw | test_commission |
| CNPJ Commission | ✅ validators | test_commission |
| Parcelas vs total contrato | 🟡 Parcial — sync cria Payments; soma não sempre validada vs current_value | 🟡 |
| `end_date >= start_date` | 🟡 Verificar Deadline/Contract — nem todos validam | 🟡 |
| Status inválido Cancelled→Open | 🟡 Frappe Select permite edição manual | 🟡 Baixo |
| CPF/CNPJ Customer | ✅ validators.py | test_customer |

### Inconsistências

1. 🟡 **Vocabulário status misto** EN/PT entre Commission (EN) e Payment (PT) — relatórios precisam mapear.
2. 🟡 **Soma parcelas vs valor contrato** — sem assert explícito pós-aditivo em todos os caminhos.
3. 🟢 **Rollups principais** cobertos por testes e hooks.

---

*Auditoria somente leitura.*

*Última atualização: 2026-06-23 23:24 UTC — app v1.1.0*
