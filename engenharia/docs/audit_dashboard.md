# Seção 4 — Verificação do Painel (Dashboard)

**Page:** `eng-dashboard` (`engenharia/engenharia/page/eng_dashboard/`)  
**Backend:** `engenharia/dashboard/` · **Facade:** `dashboard_api.py`  
**Nota:** Prompt referencia `painel_eng/` — **não existe**; implementação atual é `eng_dashboard`.

---

## 4.1 Backend

### Módulos e responsabilidades

| Módulo | Função |
|---|---|
| `__init__.py` | Orquestrador `get()` |
| `kpis.py` | KPIs agregados |
| `financial.py` | Fluxo, gráficos, pagamentos pendentes |
| `deadlines.py` | Prazos, alertas, centro_atencao |
| `attention.py` | Tiles de ação imediata |
| `health.py` | Score operacional |
| `timeline.py` | Tarefas, comunicações, horas |
| `agenda.py` | Timeline unificada |
| `_helpers.py` | Caps, normalização, `user_is_engenharia_manager()` |

### Queries principais (todas com LIMIT via `LIST_LIMIT_MAX=100` ou cap explícito)

| Origem | DocType(s) | Limit |
|---|---|---|
| kpis (manager) | Payment, Work Cost, Reimbursable Expense, Engineering Contract | 100 |
| kpis (operacional) | Construction Project, Deadline, Task, Permit, Customer | count/get_all capped |
| financial | Payment, Reimbursable Expense | 100 |
| deadlines | Deadline | list_cap (5–15) |
| timeline | Task, Communication Log, Time Log | 100 |

**N+1:** Evitado em lookups de cliente/projeto via dict batch em `_helpers.py`. ✅

**Tempo estimado (50 projetos / 200 medições / 100 contratos):** 🟡 **2–8 s** para Manager (múltiplos get_all Payment/Work Cost). User operacional: **< 2 s** (sem queries financeiras).

### Role check `is_manager`

```python
user_is_engenharia_manager() → Engenharia Manager | System Manager | Administrator
```

**Engenharia User — chaves OMITIDAS do payload:**
- `financeiro`, `parcelas`, `pagamentos`, `despesas_pendentes`, `total_despesas_mes`
- KPIs financeiros: `amount_receivable`, `amount_overdue`, `amount_reimbursable`, `month_costs`, `received_*`, `active_contracts`, `spec_project_total`, etc.
- Tiles financeiros em `atencao` (parcelas vencidas, custos pendentes)
- Pagamentos na agenda/timeline

**Chaves SEMPRE presentes:** `kpis` (operacional), `deadlines`, `tarefas`, `timeline`, `horas_*`, `is_manager`, `alertas`, `atencao` (sem tiles financeiros).

| Verificação | Status |
|---|---|
| User não recebe `financeiro` | ✅ test_permissions |
| Manager recebe financeiro completo | ✅ |
| `agent_api.get_project_summary` ainda expõe financeiro a User com read no projeto | 🟡 Gap separado (Seção 7) |

---

## 4.2 Frontend

**Shell:** `eng_dashboard.js` → módulos em `public/js/dashboard/`

| Componente | Role Manager | Role User |
|---|---|---|
| Hero + filtros | ✅ | ✅ |
| Attention tiles | Todos | Sem tiles financeiros |
| Timeline/agenda | Com pagamentos | Sem pagamentos |
| Zona financeira (health, kpis, financial, lists) | ✅ Renderiza | ✅ `$financeZone.remove()` — sem espaço vazio |
| CSS cores | `dashboard.css` usa CSS vars | ✅ |
| Hex hardcoded | Fallback `#fff` apenas | 🟢 Baixo |

**Responsividade:** CSS grid em `dashboard.css` — 🟡 não auditado em browser <768px; layout provavelmente empilha (verificar manualmente).

**Links clicáveis:** Tiles usam `deep_link: {doctype, filters}` — ✅ padrão pagamento/deadline/task.

---

## 4.3 Dados de teste no site dev

**Estado atual `engenharia.local` (consulta 2026-06-06):**

| Entidade | Quantidade | Nota |
|---|---|---|
| Construction Project | 1 (Orçamento) | Insuficiente para cenário 3 projetos |
| Commission | 1 | OK parcial |
| Deadline | 1 | Insuficiente |
| Task | 2 | OK parcial |
| Engineering Contract | (não contado) | — |

**Recomendação:** Criar dataset mínimo do prompt (3 projetos, 2 contratos, 3 deadlines, etc.) para smoke visual — **não executado nesta auditoria** (somente leitura).

---

## Inconsistências

1. 🟡 Nome da page `eng-dashboard` vs prompt `painel_eng` — documentação desatualizada.
2. 🟡 `limit_page_length` deprecated em kpis/financial.
3. 🟡 `mark_payment_received` exposto no dashboard sem role check na facade.
4. 🟢 Frontend remove zona financeira inteira para User — UX limpa.

---

*Auditoria somente leitura.*
