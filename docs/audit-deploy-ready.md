# Auditoria Deploy-Ready — Engenharia

**Data:** 2026-06-07  
**Commit:** `8adb0aef30e31911d856a45a9105c4dac8745a3c`  
**Site de referência:** `engenharia.local`  
**Norma:** `REGRAS_OBRIGATORIAS.md`

---

## Resumo

| Resultado | Quantidade |
| --- | ---: |
| ✅ Passou | 42 |
| ⚠️ Atenção (não bloqueante) | 14 |
| ❌ Bloqueante | 2 |

**Veredito:** o app está **quase pronto** para deploy em bench nativo. A suíte Python está verde (**211 testes OK**), não há Server/Client Scripts no banco, schema DocType está consistente e os três baldes de reprodutibilidade (código / fixtures / seed) estão implementados. Há **2 violações normativas** que devem ser corrigidas antes de considerar o deploy “fechado” segundo `REGRAS_OBRIGATORIAS.md`.

---

## Detalhamento por Seção

### SEÇÃO 1 — DocTypes: Schema e Naming

#### 1.1 `custom: 0`
✅ **Zero** ocorrências de `"custom": 1` em `engenharia/engenharia/doctype/*/`.

#### 1.2 `naming_rule` + `autoname`
✅ **Transacionais** (16 DocTypes): todos com `naming_rule=Expression (old style)` e `autoname=format:PREFIX-{YYYY}-{####}` (ex.: `PROJ-`, `CNTR-`, `PAY-`).

✅ **Cadastros auxiliares** (9 DocTypes): `By fieldname` + `field:<nome>` — conforme §3.4 de `REGRAS_OBRIGATORIAS.md` (Cost Category, Supplier, Stage Type, etc.).

⚠️ **Engineering Settings** (Single): `naming_rule` e `autoname` ausentes — aceitável para Single DocType, mas vale documentar explicitamente no JSON.

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

⚠️ **5** `column_break_*` sem sufixo descritivo (padrão Frappe, não auto-gerado aleatório):
- `communication_log`, `deadline`, `permit`: `column_break_info`
- `time_log`: `column_break_info`, `column_break_time`

#### 1.7 Link fields tipados
✅ Nenhuma referência real `Data`-como-`Link`. O script heurístico sinalizou campos legítimos de **nome** (`customer_name`, `supplier_name`, etc.) — falsos positivos.

#### 1.8 Prefixos de autoname — colisão
✅ **16 prefixos `format:` únicos**, sem colisão.

#### 1.9 `idx` duplicado
✅ Nenhum `idx` duplicado detectado nos JSONs de DocType.

---

### SEÇÃO 2 — Controllers Python

#### 2.1 Ordem do ciclo de vida
⚠️ Ordem **majoritariamente correta** (`validate` → `before_insert`/`after_insert` → `on_update`). Exceção observada:

- **Construction Measurement**: `after_insert` aparece **antes** de `before_save` no arquivo — inversão cosmética, sem impacto funcional conhecido.

#### 2.2 Auto-título no controller
✅ Transacionais usam `recompose_title` / `apply_title_post_insert` de `engenharia/titles.py` nos controllers (Payment, Contract, Work Cost, Permit, etc.).

✅ **Seção 5**: zero Server Scripts no banco — títulos não dependem de lógica no DB.

#### 2.3 `frappe.db.commit()` proibido
✅ **Nenhum** `frappe.db.commit()` em `engenharia/engenharia/doctype/`, APIs, `doc_events` ou scheduler.

⚠️ Ocorrências **permitidas** com comentário em `setup/*` e `patches/*` (11 arquivos).

⚠️ **`engenharia/commands.py`** (`seed-demo`, `clear-demo`): `frappe.db.commit()` sem comentário inline — aceitável como CLI de desenvolvimento, mas fora do padrão estrito §9.

#### 2.4 `ignore_permissions` sem justificativa
❌ **`engenharia/setup/permissions.py:147`** — `frappe.get_doc(doc).insert(ignore_permissions=True)` **sem comentário inline** explicando o motivo (viola §9.1 / checklist §13).

✅ Demais ocorrências em produção (`financial.py`, `calendar_sync.py`, `documents.py`, `setup/*`, `patches/*`) têm bloco ou comentário.

✅ Uso em `tests/` e `demo_data.py` com comentário de setup — aceitável.

#### 2.5 `except Exception: pass`
✅ **Zero** ocorrências de `except …: pass` silencioso.

✅ Exceções genéricas em `documents.py`, `demo_data.py`, `project_item.py` usam `frappe.log_error` ou re-raise.

#### 2.6 `eval` / `exec`
✅ **Zero** `eval(` / `exec(` em código de produção. Fórmulas usam `frappe.safe_eval`.

#### 2.7 Strings sem `_()`
⚠️ Vários `frappe.throw(` multilinha **usam** `_()` na linha seguinte — o grep heurístico (`grep -v '_('`) gera falsos positivos. Revisão manual: **sem strings PT hardcoded** evidentes em throws de produção.

#### 2.8 Whitelisted — type hints e permission check
✅ Maioria das APIs whitelisted conformes (`dashboard_api.get_dashboard_data`, `agent_api.*`, `financial.resync_contract_payments`, `documents.*`, `apply_amendment`, etc.).

❌ **Anotações ausentes** (§9.3):
| Arquivo | Função | Parâmetro(s) |
| --- | --- | --- |
| `financial.py` | `bulk_delete_payments` | `names` |
| `documents.py` | `generate_project_documents` | `template_names` |
| `dashboard_api.py` | `get_dashboard_data` | `list_limits` |
| `deadline.py` | `get_events` | `start`, `end`, `filters`, `doctype`, `field_map`, `fields` |

⚠️ **`dashboard_api.mark_payment_received`**: facade sem `has_permission` explícito — permissão validada em `dashboard/financial.py` (delegação OK, mas frágil se refatorada).

⚠️ Métodos de instância (`TimeLog.start_timer`, `Task.complete`) usam `self.check_permission("write")` — conforme, embora o AST não detecte `has_permission`.

#### 2.9 N+1 queries
⚠️ Heurística estática apontou possíveis loops com `get_value`/`get_doc` em relatórios e dashboard. **Revisão manual priorizada:** `agent_api.get_active_projects` e `dashboard/_helpers.py` fazem batch lookup — padrão correto. Nenhum N+1 **crítico** confirmado em fluxo de painel/contrato.

#### 2.10 `limit_page_length` em queries
⚠️ **`project_margin.py:115`**: `frappe.get_all("Construction Project", …, limit=0)` — sem cap explícito (relatório script; risco em sites com muitas obras).

⚠️ Outras queries em reports usam filtros por projeto/período — risco moderado.

---

### SEÇÃO 3 — JavaScript Client-Side

#### 3.1 `cur_frm` (API deprecada)
✅ **Zero** ocorrências em `public/` e `doctype/*/`.

#### 3.2 Hex hardcoded
⚠️ **1 ocorrência** em `public/css/dashboard.css:185` — fallback `var(--white, #fff)`. Baixo impacto visual; preferir remover hex conforme §9.

✅ **Zero** hex em arquivos `.js` de dashboard/forms.

#### 3.3 Strings sem `__()`
✅ JS de produção usa `__()` nos alerts verificados (ex.: `dashboard/lists.js`).

#### 3.4 APIs deprecadas
✅ **Zero** `$c_obj`, `add_fetch` em JS de produção.

---

### SEÇÃO 4 — hooks.py

#### 4.1 Fixtures — filtros
✅ `fixtures` definido com filtros para Workspace, Notification, Print Format, Custom Field (Event + `custom_source%`), Role, Kanban Board.

#### 4.2 Fixture JSONs exportados
✅ Diretório **`engenharia/fixtures/`** (padrão Frappe app-level) contém:
- `custom_field.json`, `kanban_board.json`, `notification.json`, `print_format.json`, `role.json`

⚠️ Workspace **não** exportado em `fixtures/` — sincronizado via **`setup/workspace.py`** + JSON em `engenharia/engenharia/workspace/` (balde 1 + seed). Consistente com REGRAS §6, mas o hook declara fixture Workspace que pode depender de export manual.

#### 4.3 `doc_events` — um handler por evento
✅ Nenhum DocType com dois handlers no mesmo evento. Pares verificados: Engineering Contract, Payment, Deadline, Permit, Project Stage, Reimbursable Expense, Installment.

#### 4.4 `scheduler_events`
✅ `daily`: `engenharia.tasks.check_overdue_installments` — função existe em `tasks.py`.

#### 4.5 `after_migrate` / seed idempotente
✅ Cadeia `after_migrate` com 9 handlers `ensure_*` / `seed_*`.

✅ Funções de seed usam `if not frappe.db.exists(...)` (ex.: `setup/seed.py`, `setup/roles.py`, `setup/reports.py`).

---

### SEÇÃO 5 — Zero Lógica no Banco

#### 5.1 Server Scripts
✅ **`bench --site engenharia.local execute frappe.get_all('Server Script', …)`** retornou lista vazia — zero Server Scripts.

#### 5.2 Client Scripts
✅ **`bench --site engenharia.local execute frappe.get_all('Client Script', …)`** retornou lista vazia — zero Client Scripts.

---

### SEÇÃO 6 — Testes

#### 6.1 Testes existem
✅ **`bench --site engenharia.local run-tests --app engenharia`**: **211 testes, OK** (25,8 s).

⚠️ Apenas **2** pastas de DocType com `test_*.py` local (`permit_type`, `document_kit`). Cobertura principal está centralizada em **`engenharia/tests/`** (38+ módulos) — padrão aceitável para o app.

#### 6.2 Testes com corpo `pass`
✅ Nenhum `def test_*` com corpo apenas `pass` detectado.

#### 6.3 Whitelisted sem teste dedicado
⚠️ Várias whitelisted (ex.: `bulk_delete_payments`, `get_events`, `generate_project_documents`) não têm teste unitário **nomeado** 1:1 — cobertura indireta via testes de domínio (`test_financial`, `test_documents`, `test_dashboard`). Recomendado reforço, não bloqueante para deploy.

---

### SEÇÃO 7 — Workspace

#### 7.1 Content vs shortcuts
⚠️ **Parcialmente sincronizado** (formato Frappe v16):

| Origem | Links |
| --- | --- |
| Content (5 shortcuts) | eng-dashboard, Construction Project, Payment, Deadline, Commission |
| Sidebar `links` | eng-dashboard, Construction Project, Payment, Commission |
| `shortcuts` | eng-dashboard, Construction Project, Payment, Deadline, Commission |

⚠️ **Deadline** aparece no content/shortcuts mas **não** na lista `links` da sidebar do workspace exportado — inconsistência operacional menor.

---

### SEÇÃO 8 — Formatação e Versionamento

#### 8.1 Tabs vs Spaces (Python)
✅ **Zero** arquivos `.py` em `engenharia/engenharia/` com indentação de 4 spaces no início de linha (grep `^ {4}`).

#### 8.2 Dead code markers
✅ **Zero** `TODO`, `FIXME`, `HACK`, `XXX`, `DEPRECATED` em `.py`/`.js` de produção (excl. docs de auditoria).

---

### SEÇÃO 9 — Reinstall Test (Simulação)

#### 9.1 Três baldes

| Balde | Conteúdo | Status |
| --- | --- | --- |
| **1 — Código** | 42 DocTypes, Page `eng_dashboard`, 5 Script Reports | ✅ |
| **2 — Fixtures** | 5 JSONs em `engenharia/fixtures/` | ✅ |
| **3 — Seed** | `after_install` + 9 handlers `after_migrate` | ✅ |

✅ DocTypes do app **não** estão em fixture (conforme REGRAS §6).

⚠️ Demo seed (`setup/demo_data.py`) existe — uso restrito a dev/CLI (`bench seed-demo`), não roda em `after_migrate` de produção.

---

## Gate de Deploy (REGRAS §12)

| Gate | Resultado |
| --- | --- |
| `run-tests --app engenharia` | ✅ 211 OK |
| `install-app` + `migrate` | ✅ (site `engenharia.local` operacional) |
| Painel / dashboard API | ✅ smoke E2E recente (`PLAYWRIGHT_*`) |
| E2E Playwright (`e2e/`) | ✅ 26/26 passos (sessão 2026-06-07) |
| Zero lógica no banco | ✅ |
| Conformidade normativa estrita | ❌ 2 itens (§ abaixo) |

---

## Ações Necessárias

### ❌ Bloqueantes (corrigir antes do deploy “fechado”)

1. **`setup/permissions.py:147`** — adicionar comentário inline justificando `ignore_permissions=True` na criação de `Custom DocPerm` (padrão `setup/install.py` / `setup/roles.py`).

2. **Whitelisted sem type hints** — adicionar anotações em:
   - `financial.bulk_delete_payments(names: str | list)`
   - `documents.generate_project_documents(..., template_names: str | list)`
   - `dashboard_api.get_dashboard_data(..., list_limits: dict | None = None)`
   - `deadline.get_events(start: str, end: str, ...)`

### ⚠️ Recomendadas (pós-deploy ou sprint curta)

1. Incluir **Deadline** nos `links` do workspace sidebar ou remover do content — alinhar navegação.
2. Remover fallback `#fff` em `dashboard.css` ou substituir por variável Frappe pura.
3. Cap explícito em `project_margin` (`limit=0` → limite razoável ou paginação).
4. Comentário em `commands.py` nos `commit()` de seed-demo/clear-demo.
5. Testes dedicados para whitelisted críticas (`bulk_delete_payments`, geração de documentos).
6. Renomear `column_break_info` duplicados para sufixos descritivos (cosmético).

---

*Auditoria diagnóstica — nenhum arquivo de código foi alterado durante esta verificação.*
