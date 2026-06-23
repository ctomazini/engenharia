# Seção 4 — Verificação do Painel (Dashboard)

**Page:** `eng-dashboard` (`engenharia/engenharia/page/eng_dashboard/`)  
**Backend:** `engenharia/dashboard/` · **Facade:** `dashboard_api.py`  
**Versão app:** 1.1.0  
**Revisão:** 2026-06-23 — `budget_overview` + `margin_by_project` (Manager); composição em barras CSS.

---

## 4.1 Backend

### Módulos e responsabilidades

| Módulo | Função |
|---|---|
| `__init__.py` | Orquestrador `get()` |
| `kpis.py` | KPIs agregados (`month_costs`: Work Cost + Subcontract Payment só `funded_by=Escritório`) |
| `financial.py` | Fluxo mensal fixo, composição por categoria, pagamentos pendentes no período |
| `budget_margin.py` | **Orçado vs Realizado** e **Margem por Obra** (top 10, visão acumulada) |
| `deadlines.py` | Prazos, alertas, centro_atencao |
| `attention.py` | Tiles de ação imediata |
| `health.py` | Score operacional |
| `timeline.py` | Tarefas, comunicações, horas |
| `agenda.py` | Timeline operacional (prazos + tarefas; **sem pagamentos**) |
| `operational.py` | Obras ativas enriquecidas |
| `subcontracts.py` | KPIs subcontratos |
| `commissions.py` | Lista comissões no painel |
| `_helpers.py` | Caps, normalização, `user_is_engenharia_manager()` |

### Payload Manager — chaves financeiras analíticas (v1.1.0)

| Chave | Conteúdo |
|---|---|
| `budget_overview` | `{ items[], totals{} }` — orçado, realizado, desvio, % usado |
| `margin_by_project` | `{ items[], totals{} }` — recebido, pago, margem, margin_pct |

Reutiliza `build_consolidated_costs_summary_batch` (3 queries batch). **Não** depende de `period_days`.

### Role check `is_manager`

```python
user_is_engenharia_manager() → Engenharia Manager | System Manager | Administrator
```

**Engenharia User — chaves OMITIDAS:** `financeiro`, `budget_overview`, `margin_by_project`, parcelas, despesas, KPIs financeiros.

---

## 4.2 Frontend

**Shell:** `eng_dashboard.js` → módulos em `public/js/dashboard/`

| Componente | Manager | User |
|---|---|---|
| Hero + filtros período | ✅ | ✅ |
| Zona atenção + próximos compromissos | ✅ | ✅ |
| Agenda / timeline | ✅ | ✅ |
| Obras ativas | ✅ | ✅ |
| Zona financeira (KPIs, fluxo, orçado, margem) | ✅ | Hint de permissão |
| Listas parcelas / reembolsáveis / escritório | ✅ | Oculto |
| Comissões | ✅ | Oculto |

**Módulos JS:** `hero`, `attention`, `next_event`, `timeline`, `operational`, `health`, `kpis`, `financial`, **`budget_margin`**, `lists`, `commissions`, `utils`, `filters`, `quick_actions`.

**Financeiro (Manager):**
- `fluxo` = mês corrente fixo (`fixed_to_month: true`)
- `grafico` / `grafico_office` = barras horizontais CSS por categoria
- `budget_margin.js` = barras CSS com cores condicionais (sem Chart.js)
- Refresh parcial por período **não** inclui orçado/margem (acumulado)

**CSS:** `dashboard.css` — CSS vars Frappe, `.eng-dash-chart-row`, `.eng-dash-budget-margin-host`

---

## 4.3 Testes

- `test_permissions` — User sem `financeiro`
- `test_dashboard` — contrato payload Manager
- Suíte total: **320** testes

---

*Última atualização: 2026-06-23 23:24 UTC*
