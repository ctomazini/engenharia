# Seção 4 — Verificação do Painel (Dashboard)

**Page:** `eng-dashboard` (`engenharia/engenharia/page/eng_dashboard/`)  
**Backend:** `engenharia/dashboard/` · **Facade:** `dashboard_api.py`

---

## 4.1 Backend

### Módulos e responsabilidades

| Módulo | Função |
|---|---|
| `__init__.py` | Orquestrador `get()` |
| `kpis.py` | KPIs agregados (`month_costs`: Work Cost + Subcontract Payment só `funded_by=Escritório`) |
| `financial.py` | Fluxo mensal fixo, composição por categoria, pagamentos pendentes no período |
| `deadlines.py` | Prazos, alertas, centro_atencao |
| `attention.py` | Tiles de ação imediata |
| `health.py` | Score operacional |
| `timeline.py` | Tarefas, comunicações, horas |
| `agenda.py` | Timeline operacional (prazos + tarefas; **sem pagamentos**) |
| `operational.py` | Obras ativas enriquecidas |
| `_helpers.py` | Caps, normalização, `user_is_engenharia_manager()` |

### Queries principais (LIMIT via `LIST_LIMIT_MAX=100` ou cap explícito)

| Origem | DocType(s) | Limit |
|---|---|---|
| kpis (manager) | Payment, Work Cost + Subcontract (`funded_by=Escritório`), Reimbursable Expense, Engineering Contract | 100 |
| kpis (operacional) | Construction Project, Deadline, Task, Permit, Customer | count/get_all capped |
| financial | Payment (período), Work Cost + Subcontract Payment (mês, escritório) | 100 |
| deadlines | Deadline | list_cap (5–15) |
| timeline | Task, Communication Log, Time Log | 100 |
| operational | Construction Project | list_cap `operational` |

**N+1:** Evitado em lookups de cliente/projeto via dict batch em `_helpers.py`. ✅

### Role check `is_manager`

```python
user_is_engenharia_manager() → Engenharia Manager | System Manager | Administrator
```

**Engenharia User — chaves OMITIDAS do payload:**
- `financeiro`, `parcelas`, `pagamentos`, `despesas_pendentes`, `total_despesas_mes`
- KPIs financeiros: `amount_receivable`, `amount_overdue`, `amount_reimbursable`, `month_costs`, `received_*`, etc.
- Tiles financeiros em `atencao` (parcelas vencidas, custos pendentes do escritório)

**Chaves SEMPRE presentes:** `kpis` (operacional), `deadlines`, `tarefas`, `timeline`/`agenda`, `horas_*`, `active_projects`, `is_manager`, `atencao`.

| Verificação | Status |
|---|---|
| User não recebe `financeiro` | ✅ test_permissions |
| Manager recebe financeiro completo | ✅ |
| Agenda sem pagamentos (todos os perfis) | ✅ `build_agenda` + filtro JS |
| `month_costs` exclui `funded_by=Cliente` (Work Cost + Subcontract) | ✅ test_work_cost, test_subcontract (`test_client_funded_excluded_from_cash_flow_kpis`) |

---

## 4.2 Frontend

**Shell:** `eng_dashboard.js` → módulos em `public/js/dashboard/`

| Componente | Manager | User |
|---|---|---|
| Hero + filtros período | ✅ | ✅ |
| Zona atenção + próximos compromissos (50/50) | ✅ | ✅ |
| Agenda / timeline | Prazos e tarefas | Idem |
| Obras ativas (lista `op-row`, filtro linhas) | ✅ | ✅ |
| Zona financeira | ✅ | Removida (`$financeZone.remove()`) |
| Comissões (acordeão) | ✅ | Oculto |
| Subcontratos (acordeão) | ❌ Removido | — |

**Módulos JS:** `hero`, `attention`, `next_event`, `timeline`, `operational`, `health`, `kpis`, `financial`, `lists`, `commissions`, `utils`, `filters`, `quick_actions`.

**Financeiro (Manager):**
- `fluxo.entrada` / `fluxo.saida` = mês corrente fixo (`fixed_to_month: true`)
- `grafico` = donut por categoria de custo (cores por `tone`)
- Filtros 5/10/15: delegação em `utils.bind_list_limits` → `eng_dashboard_refresh_list_sections` (sem reload total)

**CSS:** `dashboard.css` — CSS vars, grid responsivo, cards `eng-dash-atencao-card` espelhados em compromissos.

---

## 4.3 Payload — diferenças recentes

| Item | Antes | Agora |
|---|---|---|
| Subcontratos no painel | Acordeão + KPI | Apenas KPI `subcontract_outstanding` |
| Medições recentes | Seção no painel | Removida |
| Agenda | Incluía pagamentos (Manager) | Só operacional |
| Entradas × saídas | A receber total vs custos | Entradas/saídas **do mês** fixas |
| Composição custos | Fatia única azul | Fatias por **Cost Category** |
| Work Cost no caixa | Todos os lançamentos | Só `funded_by=Escritório` |
| Subcontrato no caixa | Todos os pagamentos | Só `funded_by=Escritório` |
| Saídas do mês (painel) | Só Work Cost | Work Cost + subcontratos do escritório |

---

## Inconsistências conhecidas

1. 🟡 `limit_page_length` deprecated em kpis/financial (v17).
2. 🟡 Responsividade <768px — verificar manualmente em browser.
3. 🟢 Frontend remove zona financeira inteira para User — UX limpa.

---

*Atualizado 2026-06-06.*
