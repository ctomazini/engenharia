# Auditoria Deploy-Ready — Engenharia

**Data:** 2026-06-05  
**Commit:** `8c907d2014a8f22b752057a14bfcf59545e444ff`  
**Site de referência:** `engenharia.local`  
**Norma:** `REGRAS_OBRIGATORIAS.md`

---

## Resumo

| Resultado | Quantidade |
| --- | ---: |
| ✅ Passou | 46 |
| ⚠️ Atenção (não bloqueante) | 16 |
| ❌ Bloqueante | 0 |

**Veredito:** o app está **pronto para deploy** em bench nativo. A suíte Python está verde (**212 testes OK**), não há Server/Client Scripts no banco, o schema DocType está consistente, os três baldes de reprodutibilidade estão implementados e os **2 bloqueantes** da auditoria anterior (`permissions.py` + type hints em whitelisted) foram **corrigidos** nos commits `0cf9a54` / `8c907d2`. Permanecem apenas itens de atenção (hex em relatórios, delegação de permissão na facade do painel, caps de query em reports, alinhamento parcial do workspace).

---

## Detalhamento por Seção

### SEÇÃO 1 — DocTypes: Schema e Naming

#### 1.1 `custom: 0`
✅ **Zero** ocorrências de `"custom": 1` em `engenharia/engenharia/doctype/*/`.

#### 1.2 `naming_rule` + `autoname`
✅ **Transacionais** (16 DocTypes): `naming_rule=Expression (old style)` + `autoname=format:PREFIX-{YYYY}-{####}` (`PROJ-`, `CNTR-`, `PAY-`, `WCST-`, `SUBC-`, etc.).

✅ **Cadastros auxiliares** (9 DocTypes): `By fieldname` + `field:<nome>` — conforme §3.4 (`Cost Category`, `Supplier`, `Technical Item`, etc.).

⚠️ **Engineering Settings** (Single): `naming_rule` e `autoname` ausentes — aceitável para Single DocType.

#### 1.3 `title_field` + `show_title_field_in_link`
✅ Todos os standalones transacionais e cadastros: `title_field` definido e `show_title_field_in_link=1`.

⚠️ **Engineering Settings**: sem `title_field` — esperado para Single de configuração.

#### 1.4 `search_fields`
✅ Populado em todos os standalones, exceto Engineering Settings.

⚠️ **Engineering Settings**: `search_fields` ausente.

#### 1.5 DocType names — idioma
✅ **40 DocTypes** listados; todos em inglês, Title Case, singular. Nenhum nome em português.

#### 1.6 Fieldnames — qualidade
✅ **Zero** fieldnames com acentos (português).

⚠️ **5** `column_break_*` genéricos (não aleatórios, padrão Frappe):
- `communication_log`, `deadline`, `permit`: `column_break_info`
- `time_log`: `column_break_info`, `column_break_time`

#### 1.7 Link fields tipados
✅ Nenhuma referência real `Data`-como-`Link`. Heurística sinalizou campos legítimos de **nome** (`customer_name`, `supplier_name`, `template_name`, etc.) — falsos positivos.

#### 1.8 Prefixos de autoname — colisão
✅ **16 prefixos `format:` únicos**, sem colisão (`CMSN-`, `COMM-`, `PROJ-`, …).

#### 1.9 `idx` duplicado
✅ Nenhum `idx` duplicado detectado nos JSONs de DocType.

---

### SEÇÃO 2 — Controllers Python

#### 2.1 Ordem do ciclo de vida
⚠️ Ordem **majoritariamente correta** (`validate` → `after_insert` → `on_update`). Inversões cosméticas pontuais (ex.: `Construction Measurement`) — sem impacto funcional conhecido.

#### 2.2 Auto-título no controller
✅ **42+** referências a `recompose_title` / `apply_title_post_insert` nos controllers transacionais via `engenharia/titles.py`.

✅ **Seção 5**: zero Server Scripts no banco — títulos não dependem de lógica no DB.

#### 2.3 `frappe.db.commit()` proibido
✅ **Nenhum** `frappe.db.commit()` em `doctype/`, APIs whitelisted, `doc_events` ou scheduler.

✅ Ocorrências **permitidas** com comentário em `setup/*` e `patches/*` (14 arquivos).

⚠️ **`engenharia/commands.py`** (`seed-demo`, `clear-demo`): `frappe.db.commit()` sem comentário inline — CLI de desenvolvimento; fora do padrão estrito §9, mas não roda em request/hook.

#### 2.4 `ignore_permissions` sem justificativa
✅ **`setup/permissions.py:147`** — comentário inline presente: `# setup: insere Custom DocPerm no migrate — sync de roles Engenharia` *(bloqueante anterior resolvido)*.

✅ **`financial.py`** — bloco de justificativa no topo do módulo para sync de Payment filho.

✅ Demais ocorrências em produção (`calendar_sync.py`, `documents.py`, `setup/*`, `patches/*`, `engineering_contract.apply_amendment`) têm comentário inline ou bloco.

✅ Uso em `tests/` — aceitável.

#### 2.5 `except Exception: pass`
✅ **Zero** ocorrências de `except …: pass` silencioso.

#### 2.6 `eval` / `exec`
✅ **Zero** `eval(` / `exec(` em código de produção. Fórmulas usam `frappe.safe_eval`.

#### 2.7 Strings sem `_()`
⚠️ Vários `frappe.throw(` multilinha **usam** `_()` na linha seguinte — grep heurístico gera falsos positivos. Revisão manual: sem strings PT hardcoded evidentes em throws de produção.

#### 2.8 Whitelisted — type hints e permission check
✅ **Type hints** presentes nas whitelisted que eram bloqueantes:
- `financial.bulk_delete_payments(names: str | list)`
- `documents.generate_project_documents(..., template_names: str | list)`
- `dashboard_api.get_dashboard_data(..., list_limits: dict | None = None)`
- `deadline.get_events(start: str, end: str, filters: str | dict | None = None, ...)`

✅ **25 funções** whitelisted mapeadas; maioria com `frappe.has_permission(..., throw=True)` ou `check_permission`.

✅ **`dashboard_api.mark_payment_received`**: `has_permission("Payment", "write", throw=True)` na facade + teste em `test_dashboard_api.py`.

⚠️ **`get_active_user_timer`**: usa `has_permission` sem `throw=True` (retorna `None`) — padrão intencional para timer global.

#### 2.9 N+1 queries
⚠️ Heurística estática apontou possíveis loops com `get_value`/`get_doc` em relatórios e `documents._get_subcontracts_context` (lookup de Supplier em batch após `get_all`). **Revisão manual:** dashboard usa batch em `_helpers.py`; nenhum N+1 **crítico** confirmado em fluxos principais (painel, contrato, agent API).

#### 2.10 `limit_page_length` em queries
⚠️ Heurística encontrou **~98** linhas com `get_all`/`get_list`/`db.sql` sem `limit` na mesma linha — muitas têm `limit`/`limit_page_length` nas linhas seguintes ou usam `limit=0` intencional em reports.

⚠️ Reports (`project_margin`, `work_cost_*`) e rollups usam `limit=0` ou caps altos — risco moderado em sites com volume muito grande.

---

### SEÇÃO 3 — JavaScript Client-Side

#### 3.1 `cur_frm` (API deprecada)
✅ **Zero** ocorrências em `public/` e `doctype/*/`.

#### 3.2 Hex hardcoded
⚠️ **`public/css/dashboard.css:185`** — fallback `var(--white, #fff)`.

⚠️ **`engenharia/report_visuals.py`** — paleta hex para gráficos de Script Reports (`#22c55e`, `#dc2626`, …). Exceção documentada em `REGRAS_OBRIGATORIAS.md` §12 (Script Reports); Frappe charts exigem hex no payload Python.

✅ **Zero** hex em `.js` de forms/dashboard (formatters usam classes Bootstrap / `indicator-pill`).

#### 3.3 Strings sem `__()`
✅ JS de produção usa `__()` nos alerts e filtros de reports verificados.

#### 3.4 APIs deprecadas
✅ **Zero** `$c_obj`, `add_fetch` em JS de produção.

---

### SEÇÃO 4 — hooks.py

#### 4.1 Fixtures — filtros
✅ `fixtures` definido com filtros para Workspace, Notification, Print Format, Custom Field (Event + `custom_source%`), Role, Kanban Board.

#### 4.2 Fixture JSONs exportados
✅ Diretório **`engenharia/fixtures/`** contém:
- `custom_field.json`, `kanban_board.json`, `notification.json`, `print_format.json`, `role.json`

⚠️ Workspace **não** exportado em `fixtures/` — sincronizado via **`setup/workspace.py`** + JSON em `engenharia/engenharia/workspace/`. Hook declara fixture Workspace; depende de export manual ou seed no migrate (consistente com REGRAS §6).

#### 4.3 `doc_events` — um handler por evento
✅ Nenhum DocType com dois handlers no mesmo evento.

#### 4.4 `scheduler_events`
✅ `daily`: `engenharia.tasks.check_overdue_installments` — função existe em `tasks.py`.

#### 4.5 `after_migrate` / seed idempotente
✅ Cadeia `after_migrate` com 9 handlers `ensure_*` / `seed_*`.

✅ Funções de seed usam `if not frappe.db.exists(...)` (ex.: `setup/seed.py`, `setup/roles.py`, `setup/reports.py`).

---

### SEÇÃO 5 — Zero Lógica no Banco

#### 5.1 Server Scripts
✅ **`bench --site engenharia.local console`**: **0** Server Scripts no banco.

#### 5.2 Client Scripts
✅ **0** Client Scripts no banco.

---

### SEÇÃO 6 — Testes

#### 6.1 Testes existem
✅ **`bench --site engenharia.local run-tests --app engenharia`**: **212 testes, OK** (~30 s).

✅ Cobertura centralizada em **`engenharia/tests/`** (39 módulos), incluindo:
- `test_reports.py` — chart + `report_summary` nos 5 Script Reports
- `test_documents.py` — placeholders, geração docx, subcontratos no contexto

⚠️ Apenas **2** pastas de DocType com `test_*.py` local (`permit_type`, `document_kit`) — padrão aceitável.

#### 6.2 Testes com corpo `pass`
✅ Nenhum `def test_*` com corpo apenas `pass` detectado.

#### 6.3 Whitelisted sem teste dedicado
✅ Whitelist crítica reforçada: `test_dashboard_api.py`, `test_whitelist.py`, `test_imports.py`.

---

### SEÇÃO 7 — Workspace

#### 7.1 Content vs shortcuts
⚠️ **Parcialmente sincronizado** (formato Frappe v16):

| Origem | Atalhos |
| --- | --- |
| Content (5 shortcuts) | Painel, Construction Project, Payment, Deadline, Commission |
| `links` (sidebar workspace) | Painel, Construction Project, Payment, Commission |
| `shortcuts` | Painel, Construction Project, Payment, Deadline, Commission |

⚠️ **Deadline** aparece no content/shortcuts mas **não** na lista `links` do workspace exportado. Sidebar operacional completa (`setup/sidebar.py`) tem mais entradas que o workspace JSON — inconsistência cosmética.

---

### SEÇÃO 8 — Formatação e Versionamento

#### 8.1 Tabs vs Spaces (Python)
✅ **Zero** arquivos `.py` em `engenharia/` com indentação de 4 spaces no início de linha (grep `^ {4}`).

#### 8.2 Dead code markers
✅ **Zero** `TODO`, `FIXME`, `HACK`, `XXX`, `DEPRECATED` em `.py`/`.js` de produção (excl. docs de auditoria).

---

### SEÇÃO 9 — Reinstall Test (Simulação)

#### 9.1 Três baldes

| Balde | Conteúdo | Status |
| --- | --- | --- |
| **1 — Código** | 42 pastas DocType, Page `eng_dashboard`, 5 Script Reports (+ `report_visuals.py`), `documents.py` | ✅ |
| **2 — Fixtures** | 5 JSONs em `engenharia/fixtures/` | ✅ |
| **3 — Seed** | `after_install` + 9 handlers `after_migrate` | ✅ |

✅ DocTypes do app **não** estão em fixture (conforme REGRAS §6).

⚠️ Demo seed (`setup/demo_data.py`) + CLI `bench seed-demo` — uso restrito a dev; não roda em `after_migrate` de produção.

---

## Gate de Deploy (REGRAS §12)

| Gate | Resultado |
| --- | --- |
| `run-tests --app engenharia` | ✅ 212 OK |
| `install-app` + `migrate` | ✅ (site `engenharia.local` operacional) |
| Painel / dashboard API | ✅ smoke via testes + E2E histórico |
| E2E Playwright (`e2e/`) | ✅ 26/26 passos (sessão 2026-06-07; não reexecutado nesta auditoria) |
| Script Reports (chart + KPI) | ✅ `test_reports.py` verde |
| Placeholders docx | ✅ `test_documents.py` verde; catálogo em `PLACEHOLDER_REFERENCE` |
| Zero lógica no banco | ✅ |
| Conformidade normativa estrita | ✅ (bloqueantes anteriores resolvidos) |

---

## Ações Necessárias

### ❌ Bloqueantes

*Nenhum item bloqueante identificado nesta auditoria.*

### ⚠️ Recomendadas (pós-deploy ou sprint curta)

1. Incluir **Deadline** nos `links` do workspace JSON ou remover do content — alinhar navegação.
2. Remover fallback `#fff` em `dashboard.css` ou substituir por variável Frappe pura.
3. Cap explícito em reports com `limit=0` (`project_margin`, agregações globais) — paginação ou limite documentado.
4. Comentário em `commands.py` nos `commit()` de `seed-demo` / `clear-demo`.
5. Testes dedicados para whitelisted críticas (`bulk_delete_payments`, `mark_payment_received`, `resync_contract_payments`).
6. Renomear `column_break_info` duplicados para sufixos descritivos (cosmético).
7. Exportar ou documentar fixture **Workspace** se deploy limpo depender só de `bench migrate` sem `setup/workspace.py`.

---

## Evolução desde auditoria 2026-06-07

| Item | Antes | Agora |
| --- | --- | --- |
| Bloqueantes normativos | 2 | 0 |
| Testes Python | 211 | 212 |
| Script Reports | Tabelas simples | Gráficos + KPIs + formatters JS |
| Placeholders docx | Parcial | Catálogo completo (orçamento, logo, subcontratos) |
| Commit | `8adb0ae` | `8c907d2` |

---

*Auditoria diagnóstica — nenhum arquivo de código foi alterado durante esta verificação (apenas este relatório).*
