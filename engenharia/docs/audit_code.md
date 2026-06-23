# Seção 1 — Auditoria de Código Completa

**App:** `engenharia` · **Site:** `engenharia.local` · **Versão:** 1.1.0 · **Data:** 2026-06-06  
**Referência normativa:** `REGRAS_OBRIGATORIAS.md` na raiz do app.

> **Nota 2026-06-23:** 46 DocTypes, **6** Script Reports, **320** testes, `budget_margin` no painel. Detalhes em `CODEBASE.md`.

---

## 1.1 Conformidade com checklist pré-commit

| Item | Status | Detalhes |
|---|---|---|
| DocTypes `custom: 0` | 🟢 OK | 46 DocTypes no app; lógica em controllers Python (zero Server/Client Script no banco). |
| Zero Server/Client Script no banco | 🟢 OK | Confirmado em `engenharia.local` e `advocacia.local`. |
| DocType names EN Title Case | 🟢 OK | 46/46 em inglês singular (ex.: `Office Expense`, `Construction Project`). |
| Fieldnames slug EN | 🟡 Parcial | Maioria OK. **Exceções sem sufixo auto-gerado de 4 chars**, mas nomes genéricos: `column_break_info`, `column_break_dates`, `column_break_time`, `column_break_det`, `column_break_art` (4 arquivos). Zero `table_xxxx` auto-gerado. |
| Strings dinâmicas `_()` / `__()` | 🟡 Parcial | Controllers e dashboard usam `_()`. **JS de forms** em geral sem `__()` nos labels inline (herdam do JSON). Print format HTML em fixture tem strings PT hardcoded (aceitável para template). |
| naming + autoname + title + search | 🟡 Parcial | **Engineering Settings** (Single): sem autoname/title/search — aceito para Single. **Cadastros By fieldname** usam `title_field` = campo do nome (OK). Transacionais: OK pós-correções de naming. |
| Links tipados (não Data) | 🟢 OK | Referências a entidades usam Link/Table. CPF/CNPJ/telefone em Data com normalização no controller. |
| Ciclo de vida controller | 🟢 OK | Transacionais: `validate()` + `after_insert()` com `titles.py`. Exceções documentadas: Customer (sem composição), cadastros auxiliares. |
| Auto-título via titles.py | 🟢 OK | 12+ transacionais integrados. Customer/Task usam campo descritivo direto (`customer_name`/`subject`). |
| Zero `frappe.db.commit()` fora setup | 🟢 OK | Apenas em `setup/*`, `patches/*`. **Nota:** `financial.resync_contract_payments(..., commit=True)` é whitelisted — ver segurança. |
| `ignore_permissions` com comentário | 🟡 Parcial | `financial.py`, `calendar_sync.py`, `documents.py`, `setup/*`, `patches/*` OK. **`permissions.py:144`** insert Custom DocPerm sem comentário inline. **`test_permissions.py`** e dezenas de testes usam `ignore_permissions=True` sem comentário (aceitável em testes). |
| Zero `except Exception: pass` | 🟢 OK | Não encontrado. `financial.py:381` e `formulas.py:69` capturam e re-lançam/logam. |
| Zero `eval`/`exec` | 🟢 OK | Fórmulas usam `frappe.safe_eval` em `formulas.py`. |
| Zero hex/API deprecada JS | 🟡 Parcial | **Sem `cur_frm`/`add_fetch`/`$c_obj`** em JS de produção. **`dashboard.css`**: fallback `#fff` em `var(--white, #fff)` — 🟢 Baixo. **`.eslintrc`** declara globals deprecados (não uso). |
| Whitelisted + type hints + permission | 🟡 Parcial | Ver seção 1.3. **`cancel_contract_payment`** usa `has_permission` sem `throw=True`. **`mark_payment_received`** delega sem check na facade. |
| Queries com limit; preferir qb | 🟡 Parcial | **`limit_page_length` deprecated v17**: 40+ ocorrências (ver 1.4). Maioria tem cap. **`project_rollup`/`reports`**: `limit_page_length=0` (sem limite explícito em alguns relatórios). |
| Zero N+1 | 🟡 Parcial | Dashboard usa batch lookups em `_helpers.py`. **`agent_api.get_active_projects`**: batch customer names OK. **`get_costs_by_category`**: carrega todas Cost Categories (limit 200) — OK. Possível N+1 em loops pontuais de reports — 🟢 Baixo. |
| doc_events: um handler/evento | 🟢 OK | `hooks.py` respeita um handler por par DocType+evento. |
| Vocabulário status consistente | 🟡 Parcial | Payment/Commission/Contract usam EN (`Open`, `Paid`, `Pendente` misto PT/EN). Commission status EN; Payment PT. Documentado como dívida histórica. |
| Testes com assert real | 🟡 Parcial | **`engenharia/tests/`**: 190 testes reais. **18 arquivos stub** em `doctype/*/test_*.py` com `class ...: pass` (IntegrationTestCase vazio). |
| Tabs não spaces | 🟢 OK | Amostragem `.py`/`.js` usa tabs. |
| Imports não utilizados | 🟢 OK | Sem alerta sistemático; linter limpo nos arquivos editados recentemente. |
| Dead code | 🟢 OK | Dict `COMPOSED` removido de `titles.py` na sessão anterior. |

### Inconsistências prioritárias (Seção 1)

1. 🟡 **`limit_page_length` em massa** — deprecação v17; migrar para `limit` em dashboard, tasks, documents, reports.
2. 🟡 **18 stubs de teste vazios** em pastas de DocType — duplicam cobertura ou ficam mortos.
3. 🟡 **Prefixo COMM** compartilhado: `Communication Log` (`COMM-{YYYY}`) vs histórico Commission (`CMSN` após fix) — resolvido para Commission, mas COMM ainda é ambíguo para Communication Log.
4. 🟡 **`custom: 0` explícito** faltando em 13 JSONs standalone — risco em export/import de fixtures.

---

## 1.2 Cobertura de testes

**Total suite:** 320 testes (`bench run-tests --app engenharia`, 2026-06-23).

| DocType / Módulo | Tem teste? | Nº testes* | Funcionalidades testadas | SEM teste |
|---|---|---|---|---|
| Commission | Sim | 7 | CRUD, pagamento parcial/total, overpayment, título, open_count, rollup projeto | receipt attach, permissoes role |
| Construction Project | Sim | ~18 | CRUD, título, import CSV, budget, rollup, progress | permlevel campos financeiros UI |
| Project Item | Sim | ~23 | Fórmulas, outputs, rollup, budget revision, título | on_trash rollup edge cases |
| Engineering Contract | Sim | ~20 | CRUD, parcelas, aditivos, sync pagamentos, resync | apply amendment UI flow |
| Payment | Sim | ~13 | CRUD, status, sync contrato, bulk delete | mark_payment_received whitelisted |
| Work Cost | Sim | 6 | CRUD, validações, totais | — |
| Reimbursable Expense | Sim | 8 | CRUD, sync payment | — |
| Deadline | Sim | 9 | CRUD, validações, tipos | — |
| Task | Sim | 5 | CRUD, timer básico | — |
| Permit | Sim | 6 | CRUD, tipos, datas | — |
| Time Log | Sim | 15 | Timer start/stop, título, permissões | — |
| Customer | Sim | ~13 | CPF/CNPJ, contatos, endereços | — |
| Technical Item | Sim | ~11 | Fórmulas, fields, outputs | — |
| Construction Measurement | Sim | 2 | CRUD mínimo | itens, totais |
| Communication Log | Sim | 7 | CRUD, título | — |
| Document Template / Kit | Sim | ~13 | Geração docx, kits, placeholders | — |
| Script Reports (7) | Sim | 6+ | chart + KPI via `report_visuals.py`; print formats em `test_print_formats` | — |
| Office Expense | Sim | 8 | CRUD, recorrência, scheduler, título | mark_office_expense_paid facade |
| Project Stage | Sim | 3 | CRUD, progress hook | título composto |
| Cadastros (Supplier, Cost Category, etc.) | Sim | 1–6 cada | CRUD mínimo | — |
| Engineering Settings | Sim | 3 | Seed, documents | — |
| **Child tables** (14) | Não | 0 | — | Todas (herdam teste do pai parcialmente) |
| **Dashboard** | Sim | 10 | Contrato payload, attention, health, limits | role User E2E browser |
| **Permissions** | Sim | 7 | Role matrix, dashboard redaction | — |
| **Agent API** | Sim | 4 | 3 endpoints + permission denied | — |
| **Calendar sync** | Sim | 6 | Deadline/Permit → Event | — |
| **Notifications/Scheduler** | Parcial | 1 | — | `check_overdue_installments` sem teste dedicado |
| **Financial whitelists** | Parcial | via test_financial | resync, bulk_delete | `cancel_contract_payment` |

\*Contagens aproximadas incluindo testes cross-module.

### Gaps específicos

| Área | Gap | Severidade |
|---|---|---|
| `@frappe.whitelist()` | `mark_payment_received`, `cancel_contract_payment`, `get_construction_project_spec_preview`, métodos Time Log | 🟡 |
| Scheduler | `engenharia.tasks.check_overdue_installments` | 🟡 |
| Rollup | Delete Commission → `commission_outstanding` zero (testado indiretamente em test_commission) | 🟢 |
| Permissões role | Coberto em test_permissions (novo) | 🟢 |

---

## 1.3 Segurança

| Endpoint / Área | Permission check? | Observação |
|---|---|---|
| `dashboard_api.get_dashboard_data` | Sim | `Construction Project` read + redaction `is_manager` |
| `dashboard_api.mark_payment_received` | Delegado | Check em `financial.mark_payment_received` (Payment write) |
| `agent_api.*` (3 funções) | Sim | throw=True |
| `financial.resync_contract_payments` | Sim | Engineering Contract write |
| `financial.bulk_delete_payments` | Sim | Payment delete |
| `financial.cancel_contract_payment` | Parcial | `has_permission` sem throw=True — 🟡 |
| `construction_project.*` whitelists | Sim | read no projeto |
| `project_item.*` whitelist | Sim | — |
| `engineering_contract.apply_amendment` | Sim | write no contrato |
| `time_log.start_timer/stop_timer` | Sim | — |
| `deadline.*` whitelist | Verificar arquivo | — |
| `documents.*` whitelists | Sim | Construction Project read/write |

**Dashboard financeiro:** `user_is_engenharia_manager()` omite chaves `financeiro`, `parcelas`, `pagamentos`, KPIs financeiros para Engenharia User — ✅ conforme desenho.

**Sugestões:**
- 🟡 Adicionar `throw=True` em `cancel_contract_payment` ou alinhar com padrão do app.
- 🟡 `get_project_summary` (agent_api) expõe dados financeiros a qualquer user com read no projeto — Engenharia User **não tem** read em Payment/Contract mas ainda vê agregados via API — 🟡 vazamento semântico.

---

## 1.4 Deprecation Warnings

### `limit_page_length` (v17 → usar `limit`)

| Arquivo | Ocorrências |
|---|---|
| `dashboard/kpis.py` | 9 |
| `dashboard/financial.py` | 3 |
| `dashboard/timeline.py` | 1 |
| `dashboard/__init__.py` | param exposto |
| `documents.py` | 3 |
| `construction_project.py` | 1 |
| `tasks.py` | 2 |
| `project_progress.py` | 1 |
| `project_rollup.py` | 3 |
| `financial.py` | (via get_all interno) |
| Reports (`cash_flow`, `project_margin`) | 5+ com `limit_page_length=0` |
| `print_formats/orcamento.html` | 1 |
| `fixtures/print_format.json` | 1 |

### Outras APIs deprecadas

| Padrão | Ocorrências produção |
|---|---|
| `cur_frm` | 0 |
| `add_fetch` | 0 |
| `$c_obj` | 0 (só `.eslintrc` global) |

---

*Auditoria somente leitura — nenhum código alterado.*

*Última atualização: 2026-06-23 23:24 UTC*
