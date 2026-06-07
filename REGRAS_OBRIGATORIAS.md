# REGRAS_OBRIGATORIAS.md

**App alvo:** `engenharia` (greenfield) · **Referência:** `advocacia` (brownfield Frappe v16)  
**Objetivo:** checklist operacional fechado — nada aqui é proposta em aberto.  
**Última consolidação:** 2026-06-02

---

## 1. Identidade do app

| Decisão | Regra |
| --- | --- |
| Framework | Frappe v16, **sem ERPNext** |
| DocTypes | Todos `custom: 0`, módulo único `Engenharia` |
| Versionamento | Git desde commit 0; **Conventional Commits**; **um DocType por commit** |
| Instalabilidade | `bench install-app engenharia` + `migrate` + `run-tests` verde em site limpo = pronto |

**Não copiar** nomes de DocType em português do `advocacia` — ver §2.

---

## 2. Nomenclatura (definitiva)

### 2.1 Regras

| Elemento | Idioma / formato | Exemplo |
| --- | --- | --- |
| DocType name | Inglês, Title Case, singular | `Construction Project` |
| `fieldname` | Inglês `snake_case`, slug do conceito | `project`, `cost_category` |
| Label / mensagem UI | Português via `_()` / `__()` | label: "Obra" |
| Child table | Pai + relação | `Engineering Contract Installment` |
| Roles (app) | `Engenharia User`, `Engenharia Manager` | espelhar `Advocacia User` em `setup/install.py` |

Referência de roles: `advocacia/advocacia/setup/install.py`.

### 2.2 De-para blueprint (PT conceito → EN DocType)

| Conceito (blueprint PT) | DocType EN |
| --- | --- |
| Obra | Construction Project |
| Contrato de Obra | Engineering Contract |
| Custo da Obra | Work Cost |
| Subcontrato / Prestador | Subcontract |
| Aditivo | Contract Amendment |
| Despesa Reembolsável | Reimbursable Expense |
| Item Técnico | Technical Item |
| Especificação da Obra | Project Specification |
| Etapa | Project Stage |
| Fornecedor | Supplier |
| Categoria de Custo | Cost Category |
| Órgão Público | Public Agency |
| Protocolo / Alvará | Permit |
| Pagamento (camada financeira) | Payment |
| Prazo | Deadline |
| Tarefa | Task (nativo Frappe, Kanban) |
| Cliente | Customer (nativo ou DocType próprio — decidir no primeiro commit de Customer) |

### 2.3 Advocacia vs Engenharia

| | Advocacia | Engenharia |
| --- | --- | --- |
| DocType names | PT congelado (brownfield) | EN desde o dia 0 |
| Exemplo hub | `Servico` | `Construction Project` |
| Exemplo contrato | `Acordo de Honorarios Processuais` | `Engineering Contract` |

---

## 3. Padrão de DocType transacional

Extraído de `advocacia/advocacia/doctype/acordo_de_honorarios_processuais/`.

### 3.1 JSON (obrigatório)

```json
"custom": 0,
"module": "Engenharia",
"naming_rule": "Expression",
"autoname": "format:CNTR-{YYYY}-{####}",
"title_field": "title",
"search_fields": "title,customer,status",
"show_title_field_in_link": 1,
"track_changes": 1
```

- Prefixo por domínio: obra `PROJ-`, contrato `CNTR-`, pagamento `PAY-`, custo `WCST-`, etc.
- `autoname` com **`{YYYY}`** (não só `{####}`): ver `acordo_de_honorarios_processuais.json` (`format:ACOR-{YYYY}-{####}`).

### 3.2 Controller (ciclo de vida)

Ordem em `advocacia/advocacia/doctype/acordo_de_honorarios_processuais/acordo_de_honorarios_processuais.py`:

1. `validate()` — regras de negócio, fetch de links (`customer` via `project`), composição de título  
2. `after_insert()` — `aplicar_titulo_pos_insert(self)`  
3. Métodos auxiliares privados abaixo  

Padrão de fetch hub→satélite (replicar com fieldnames EN):

```python
if not self.customer and self.project:
    self.customer = frappe.db.get_value("Construction Project", self.project, "customer")
```

### 3.3 Título visível `{ID} — {descritor}`

**Referência:** `advocacia/advocacia/titulos.py`

| Função | Quando |
| --- | --- |
| `recompor_titulo_se_vazio(doc, usar_descricao=False)` | `validate()` — garante formato após edição |
| `aplicar_titulo_pos_insert(doc)` | `after_insert()` — preenche quando `name` já existe |

**Algoritmo:**

1. Separador: `TITLE_SEPARATOR = " — "`  
2. Se `title` já começa com `{name} —`, não altera.  
3. Descritor: `customer` → nome do cliente (`get_customer_name`); senão `description`; senão fallback `doctype`.  
4. Resultado: `join_title_parts(doc.name, descritor)` → ex.: `CNTR-2026-0042 — Construtora Exemplo Ltda`  
5. Persistência: `doc.db_set("title", novo, update_modified=False)`  

**Engenharia:** criar `engenharia/engenharia/titles.py` (nome EN do módulo) com dict `COMPOSED` listando DocTypes transacionais; flag `use_description=True` só onde o descritor for campo texto (ex.: despesa), como `Despesa do Escritorio` em `titulos.py` (`COMPOSTOS`).

**JSON:** `show_title_field_in_link: 1` em todo transacional (ver fim de `acordo_de_honorarios_processuais.json`).

### 3.4 Cadastro auxiliar (rígido)

**Referência:** `advocacia/advocacia/doctype/comarca/comarca.json`

| Campo meta | Valor |
| --- | --- |
| `autoname` | `field:supplier_name` (nome legível único) |
| `title_field` | mesmo campo |
| `search_fields` | nome + filtros úteis |
| `quick_entry` | `1` quando fizer sentido |
| Campos | `reqd` + `unique` no nome; **Link** para pais (ex.: `Cost Category`, `Supplier`) |

**Proibido:** texto livre repetitivo onde existe cadastro (comarca/vara no advocacia → `Public Agency`, `Cost Category`, `Project Stage` no engenharia).

---

## 4. Padrão de List View

**Referência mínima:** `advocacia/advocacia/doctype/servico/servico_list.js`  
**Referência completa (indicadores + formatters):** `advocacia/advocacia/doctype/pagamento/pagamento_list.js`

### 4.1 Obrigatório em transacionais com `title_field`

```javascript
frappe.listview_settings["Construction Project"] = {
	...(frappe.listview_settings["Construction Project"] || {}),
	hide_name_column: true,
};
```

- Coluna principal = `title` (já traz `ID — descritor`); **não** duplicar coluna `name`.

### 4.2 Recomendado

| Recurso | Uso | Referência |
| --- | --- | --- |
| `get_indicator(doc)` | Status como badge colorido; tirar `status` de `in_list_view` no JSON | `pagamento_list.js` |
| `add_fields` | Campos usados só no formatter/indicador | `pagamento_list.js` |
| `formatters` | Links derivados (ex.: origem do pagamento) | `pagamento_list.js` |
| `onload` + `add_inner_button` | Filtros rápidos operacionais | `pagamento_list.js` |

Labels nos botões/filtros: sempre `__("...")`.

---

## 5. Painel / Dashboard

### 5.1 Decisões fechadas

| Item | Regra |
| --- | --- |
| Tipo | **Page custom** (`page/dashboard/`), 100% código, reinstala no `migrate` |
| Proibido | Number Card, Dashboard Chart nativos, fixture de Page |
| Backend | Subpacote `engenharia/engenharia/dashboard/` |
| Facade | `dashboard_api.py` na raiz do pacote Python — **único** path de `xcall` |
| Frontend | `public/js/dashboard/` modular; Chart.js com **CSS variables** (sem hex no JS) |

### 5.2 Backend modular (espelho real de `painel/`)

**Referência:** `advocacia/advocacia/painel/__init__.py` (orquestrador `get()`)

| Arquivo advocacia | Linhas* | Responsabilidade | Arquivo engenharia |
| --- | ---: | --- | --- |
| `__init__.py` | 110 | `get()`, permissão, caps, monta payload | `dashboard/__init__.py` |
| `_helpers.py` | 86 | lookups em lote, normalização de limites | `dashboard/_helpers.py` |
| `kpis.py` | 181 | KPIs agregados | `dashboard/kpis.py` |
| `financeiro.py` | 275 | parcelas/pagamentos, despesas | `dashboard/financial.py` |
| `prazos.py` | 177 | prazos, audiências → deadlines/permit | `dashboard/deadlines.py` |
| `timeline.py` | 249 | timeline, tarefas, comunicações | `dashboard/timeline.py` |
| `painel_api.py` | 26 | facade whitelisted | `dashboard_api.py` |

\*Linhas atuais no repo; **meta de design ≤150 linhas/arquivo** — se passar, dividir subdomínio (ex.: `financial_payments.py`).

**Contrato do orquestrador** (`painel/__init__.py`):

1. `frappe.has_permission` no hub (`Servico` read → `Construction Project` read)  
2. Normalizar `periodo_dias`, `list_limits`, `limit_page_length` (cap 100)  
3. Chamar `_build_*` por domínio; **uma** query em lote por lookup (`_servico_lookup`, `_cliente_nome_lookup` em `_helpers.py`)  
4. Retornar dict estável de chaves (front depende disso — não renomear sem versionar)  
5. **Zero** `frappe.db.commit()` no `get()`

**Facade** (`painel_api.py`):

```python
@frappe.whitelist()
def get_dashboard_data(...):
    return _get_dashboard_data(...)
```

Front: `frappe.xcall("engenharia.engenharia.dashboard_api.get_dashboard_data", {...})` — path fixo, nunca chamar submódulos direto.

### 5.3 Frontend

- Page JS em `page/dashboard/dashboard.js` (shell + bootstrap).  
- Módulos em `public/js/dashboard/` (`kpis.js`, `timeline.js`, …).  
- Cores: variáveis CSS (padrão pós-auditoria em `painel.js`; evitar `#RRGGBB` em Chart.js).  
- JS: render + UX apenas; dados vêm do `xcall`.

### 5.4 Sidebar v16

**Referência:** `advocacia/advocacia/setup/sidebar.py` — `SIDEBAR_SECTIONS` com **`collapsible: 1`** em Section Breaks com filhos (senão scroll do desk trava no Frappe v16).

---

## 6. Reprodutibilidade — os 3 baldes

### Balde 1 — Código (install automático)

Inclui: DocTypes JSON+py+js, `hooks.py`, `public/js/`, Page `dashboard/`, Script Reports em `engenharia/report/`, `patches/`, testes.

**Não** colocar DocType do próprio app em fixture.

### Balde 2 — Fixtures (`hooks.py`)

**Referência:** `advocacia/hooks.py`

| `dt` | Filtro típico |
| --- | --- |
| Workspace | `name = Engenharia` |
| Notification | nomes configuráveis |
| Custom Field | DocTypes **nativos** (ex.: `Event`, `Task`) com prefixo `custom_` |
| Kanban Board | board de obra sobre `Task` |
| Translation | se exportar |
| Role | opcional se não criar só via seed |

### Balde 3 — Seed idempotente (`after_install` / `after_migrate`)

**Referência:** cadeia em `advocacia/hooks.py` `after_migrate`:

```python
after_migrate = [
    "engenharia.engenharia.setup.reinstall_child_doctypes",  # se aplicável
    "engenharia.engenharia.setup.install.after_install",
    "engenharia.engenharia.setup.install.ensure_*_custom_fields",
    "engenharia.engenharia.setup.translations.ensure_doctype_translations",
    "engenharia.engenharia.setup.sidebar.ensure_engenharia_sidebar",
    "engenharia.engenharia.setup.reports.ensure_engenharia_reports",
    "engenharia.engenharia.setup.workspace.ensure_engenharia_workspace",
]
```

**Padrão idempotente** (todos os `setup/*.py`):

- `if not frappe.db.exists(...):` antes de criar  
- `ensure_*` pode rodar em migrate sem duplicar  
- `frappe.db.commit()` **somente** em `setup/` e `patches/` (com comentário), nunca em API/scheduler  
- Roles: `ignore_permissions=True  # setup: cria roles durante install` — ver `setup/install.py`  
- Reports sync: comentários em `setup/reports.py`  

**Proibido:** `setup/seed_demo.py` em produção (advocacia mantém só dev).

---

## 7. Arquitetura de domínio (blueprint fechado)

### 7.1 Hub-and-spoke

```
Construction Project (hub)
    ├── Engineering Contract (+ Contract Amendment child)
    ├── Work Cost (cost_category, supplier, stage Links) — lançamento avulso
    ├── Subcontract (+ Subcontract Payment child) — contrato com prestador
    ├── Reimbursable Expense
    ├── Project Specification (child: Technical Item + value + unit)
    ├── Deadline / Permit
    └── Payment (camada financeira única)
```

- Satélites carregam `project` (Link) + `customer` (Link ou `fetch_from` project).  
- **Payment** único para recebíveis (parcelas de contrato) e fluxos derivados — espelhar `Pagamento` + `financeiro.py`.

### 7.2 Especificações (EAV controlado)

| DocType | Papel |
| --- | --- |
| Technical Item | Cadastro rígido do item (nome, unidade padrão, tipo) |
| Project Specification | Child no projeto: Link → Technical Item + `value` + `unit` |

**Por que não texto livre nem Custom Field:** agregação, relatórios e placeholders docx estáveis; mesmo princípio de Comarca/Vara no advocacia.

### 7.3 Custos

`Work Cost` por lançamento avulso com:

- `cost_category` → Cost Category  
- `supplier` → Supplier  
- `stage` → Project Stage  
- `funded_by` → Escritório (fluxo de caixa) / Cliente (só registro na obra)

Habilita relatórios por categoria / fornecedor / etapa / total.

`Subcontract` para contratos com prestador (valor acordado + parcelas):

- `total_value`, `total_paid`, `outstanding`, child `Subcontract Payment`  
- `funded_by` → Escritório (KPIs, caixa, margem realizada) / Cliente (obra apenas)  
- Margem: leitura dupla — `Work Cost` (Pago) + `Subcontract.total_paid` **do escritório** (sem sync entre DocTypes); `funded_by=Cliente` excluído do caixa via `office_subcontract_filters()` em `work_costs.py`  
- Aditivo: edição direta de `total_value` + `amendment_remarks`

### 7.4 Administração de obra

| Visão | Implementação |
| --- | --- |
| Kanban | Kanban Board sobre **Task** (fixture), colunas = etapas |
| Lista % avanço | **Project Stage** (cadastro com `progress_percent`) |

### 7.5 Contract Amendment (aditivo)

- Child table de `Engineering Contract`.  
- `validate()`: `current_value = base + Σadditions − Σreductions`.  
- Botão **"Aplicar Aditivo"** → `frappe.confirm` com **duas** opções:  
  - (a) regerar parcelas futuras preservando recebidas  
  - (b) apenas registrar histórico  
- Sync de Payment: copiar padrão `sincronizar_pagamentos_do_acordo` + flag `frappe.flags.in_payment_sync` — `advocacia/advocacia/financeiro.py`.

### 7.6 Reembolsáveis

`Reimbursable Expense`: pago pelo escritório, devolvido pelo cliente — fluxo separado de `Work Cost` (custo de obra).

### 7.7 Prazos de prefeitura

| DocType | Uso |
| --- | --- |
| Deadline | tipo inclui **"Órgão"**; Link `public_agency` |
| Permit | satélite: alvará, habite-se, ART/RRT, etc. |

Calendar sync opcional: espelhar `calendar_sync.py` → `Event` nativo.

### 7.8 Documentos

- Reusar gerador **docxtpl** (`advocacia/advocacia/documentos.py`).  
- Catálogo único em `engenharia/documents.py` → `PLACEHOLDER_REFERENCE`; UI **Ver Placeholders** no **Document Template** renderiza a lista via `get_placeholder_reference`.  
- Grupos: escritório (incl. logo/banco), cliente, endereço, contato, obra, orçamento (`project_items`), subcontratos (agregados + loops), contrato (condicional), data.  
- Nome de arquivo: `{tipo}_{project}_{date}.docx`.  
- Whitelist: `frappe.has_permission` antes de gerar — ver `documents.py`.

---

## 8. Financeiro e sync (referência `financeiro.py`)

| Padrão | Detalhe | Arquivo |
| --- | --- | --- |
| Hub contrato → parcelas child | Tabela de installments no contract | `acordo_de_honorarios_processuais.json` |
| ID estável por linha | `parcela_origem_id` / equivalente EN `installment_origin_id` | `financeiro.py` |
| Sync idempotente | `get_value` por origem; insert/update; cancelar órfãos | `financeiro.py` `_sincronizar_pagamentos_do_acordo_impl` |
| Flag reentrância | `frappe.flags.in_pagamento_sync` | `financeiro.py` |
| doc_events | **Um** handler `on_update` no contrato | `hooks.py` |
| ignore_permissions | Bloco de justificativa no topo + uso só em sync filho | `financeiro.py` linhas 5–12 |
| Status vocabulary | Masculino neutro único (`Recebido`, `Pendente`, …) em Payment e child | reports + painel |

**Proibido:** `frappe.db.commit()` em hooks de sync (Frappe commita o request).

---

## 9. Disciplinas não negociáveis

Extraídas da auditoria consolidada do advocacia (código atual).

| # | Regra | Verificação |
| --- | --- | --- |
| 1 | Zero `frappe.db.commit()` em whitelisted, `doc_events`, scheduler | `rg commit` fora de `setup/`, `patches/`, `seed_demo` |
| 2 | `ignore_permissions=True` só com comentário inline ou bloco de módulo | `financeiro.py`, `calendar_sync.py`, `setup/*` |
| 3 | Whitelisted: `frappe.has_permission(..., throw=True)` + type hints | `painel_api.py`, `documentos.py` |
| 4 | Zero N+1: `get_all` com `fields` + dict lookup; nunca `get_value` em loop | `painel/_helpers.py`, `painel/prazos.py` |
| 5 | Toda query com `limit_page_length` | schedulers, `notificacoes.py` |
| 6 | Preferência SQL: `frappe.qb` > `get_all` > `db.sql` parametrizado | painel |
| 7 | JS só UX (máscaras, show/hide, formatters); negócio no `.py` | doctype `*.js` |
| 8 | Sem hex hardcoded em charts/CSS no JS | usar CSS vars |
| 9 | Sem `cur_frm`, `$c_obj`, APIs deprecadas | — |
| 10 | Um handler por `(DocType, evento)` em `doc_events` | `hooks.py` |
| 11 | Scheduler: erro em um item não aborta o lote | `tasks.py` padrão por registro |
| 12 | Sem `except Exception: pass` — `frappe.log_error` + exceção tipada | — |
| 13 | Sem `eval` / `exec` | — |
| 14 | Indentação **tabs** em `.py` e `.js` | — |
| 15 | IDs (CPF/CNPJ/telefone) só dígitos no DB; email lower | `validators.py` + controllers |
| 16 | Repo público: sem credenciais, CPF/CNPJ/OAB reais, domínio prod | usar placeholders em testes |

### 9.1 `ignore_permissions` — mapa de referência advocacia

| Arquivo | Padrão |
| --- | --- |
| `financeiro.py` | Bloco módulo; sync de Payment filho |
| `calendar_sync.py` | `# sistema sincroniza Event em nome do usuário` |
| `documentos.py` | `# File anexado — write no Serviço já validada` |
| `comunicacao.py` | **Removido** em Tarefa auto — usar `has_permission("Tarefa", "create")` |
| `setup/install.py` | `# setup: cria roles...` |
| `setup/reports.py` | `# migrate: sincroniza / remove report` |
| `setup/translations.py` | `# setup: seed de traduções` |

---

## 10. O que reusar vs criar

### 10.1 Reusar (copiar/adaptar com nomes EN)

| Módulo advocacia | Destino engenharia | Notas |
| --- | --- | --- |
| `hooks.py` (estrutura) | `hooks.py` | fixtures, schedulers, doc_events, after_migrate |
| `titulos.py` | `titles.py` | dict `COMPOSED` com DocTypes EN |
| `validators.py` | `validators.py` | CPF/CNPJ/email; CNJ só se ainda aplicável |
| `financeiro.py` | `financial.py` | sync Payment ↔ installments |
| `tasks.py` | `tasks.py` | vencidos, notificações |
| `notificacoes.py` | `notifications.py` | templates email |
| `documentos.py` | `documents.py` | docxtpl + `PLACEHOLDER_REFERENCE` |
| — | `report_visuals.py` | charts/KPIs dos Script Reports |
| `calendar_sync.py` | `calendar_sync.py` | se usar Event |
| `painel/` → | `dashboard/` | renomear domínios |
| `painel_api.py` | `dashboard_api.py` | facade |
| `setup/*` | `setup/*` | install, sidebar, workspace, reports, translations |
| `public/js/masks.js`, `list_nav.js` | idem | máscaras BR genéricas |
| `tests/test_setup.py`, padrão CRUD | `tests/` | factories com hash único |

### 10.2 Não reusar (domínio jurídico)

| Advocacia | Motivo |
| --- | --- |
| `audiencia`, `controle_de_prazos` (jurídico) | Substituir por `Deadline` + `Permit` |
| `registro_de_atos`, `ato_advocaticio` | Sem equivalente em obra |
| `acordo_de_honorarios` (nome/campos) | Virar `Engineering Contract` |
| `servico` (campos CNJ, vara, comarca) | Virar `Construction Project` |
| `comarca`, `vara`, `tribunal`, `fase_processual` | Virar cadastros de obra |
| `parcela_de_honorarios` | Renomear conceito para installment child |
| DocTypes e reports com filtro jurídico | Reescrever queries para `Payment` + `Work Cost` |

---

## 11. hooks.py — template engenharia

Espelhar `advocacia/hooks.py`:

```python
fixtures = [Workspace, Notification, Custom Field em nativos, Kanban Board, ...]
app_include_js = [masks, list_nav, ...]  # + dashboard assets se global
scheduler_events = {"daily": [...], "weekly": [...]}
doc_events = {
    "Engineering Contract": {"on_update": "....financial.sync_payments_hook"},
    "Contract Installment": {"on_update": "....tasks.on_installment_update"},
    "Payment": {"on_update": "...", "on_trash": "..."},
}
after_install = "engenharia.engenharia.setup.install.after_install"
after_migrate = [ ... cadeia ensure_* ... ]
```

---

## 12. Testes e Definition of Done

| Gate | Comando / critério |
| --- | --- |
| Unit/integration | `bench --site <site> run-tests --app engenharia` — verde |
| E2E Desk (opcional) | `cd e2e && E2E_PASS=… npm test` — ver `e2e/README.md` |
| Site limpo | `install-app` + `migrate` sem erro |
| Painel | `xcall` dashboard retorna todas as chaves; smoke manual |
| Script Reports | `test_reports.py` verde após mudanças em `engenharia/engenharia/report/` ou `report_visuals.py` |
| Placeholders docx | `test_documents.py` verde após mudanças em `documents.py` |
| Sidebar | 26-ish links alinhados workspace ↔ sidebar; seções `collapsible: 1` |
| Um commit | Um DocType (json + py + js + test CRUD mínimo) |

**Padrão de teste:** `tearDown` → `frappe.db.rollback()`; CNPJ/CPF únicos (`_gerar_cnpj_valido()`); títulos no formato `ID — descritor` — ver `tests/test_titulos.py`.

---

## 13. Checklist pré-commit

Use como gate antes de cada commit (uma linha = uma verificação).

- [ ] Apenas **um** DocType novo/alterado por commit (escopo do commit)
- [ ] DocType: `custom: 0`, `naming_rule: Expression`, `autoname: format:PREFIX-{YYYY}-{####}`
- [ ] DocType transacional: `title_field: title`, `show_title_field_in_link: 1`, `search_fields` preenchido
- [ ] Controller: `validate` compõe título via `titles.py`; `after_insert` chama `apply_title_post_insert`
- [ ] Fieldnames em **inglês** `snake_case`; labels em **português** com `_()`
- [ ] Links para cadastros rígidos (nunca `Data` para conceito repetitivo)
- [ ] `*_list.js`: `hide_name_column: true` se usa `title_field`
- [ ] JS do form: só UX; sem regra de negócio exclusiva no client
- [ ] Python: validações com `frappe.throw` no controller
- [ ] Sem `frappe.db.commit()` fora de `setup/` e `patches/`
- [ ] `ignore_permissions` só com comentário justificando
- [ ] Whitelisted novos: `has_permission` + type annotations
- [ ] Queries novas com `limit_page_length`; sem N+1
- [ ] `doc_events`: um handler por evento; path em `hooks.py`
- [ ] Teste CRUD ou caso feliz do DocType incluído no commit
- [ ] `bench migrate` + `run-tests --app engenharia` verdes
- [ ] Sem segredos/dados reais no diff; sem alterar só `modified` de Report exportado
- [ ] Conventional Commit: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`

---

## 14. Referência rápida de arquivos advocacia

| Tópico | Caminho |
| --- | --- |
| Hooks / fixtures | `advocacia/hooks.py` |
| Títulos | `advocacia/advocacia/titulos.py` |
| Dashboard backend | `advocacia/advocacia/painel/` |
| Dashboard facade | `advocacia/advocacia/painel_api.py` |
| Dashboard page | `advocacia/advocacia/page/painel/painel.js` |
| Validators | `advocacia/advocacia/validators.py` |
| Sync financeiro | `advocacia/advocacia/financeiro.py` |
| Setup / seed | `advocacia/advocacia/setup/` |
| DocType transacional | `advocacia/advocacia/doctype/acordo_de_honorarios_processuais/` |
| Cadastro auxiliar | `advocacia/advocacia/doctype/comarca/comarca.json` |
| List view | `advocacia/advocacia/doctype/pagamento/pagamento_list.js` |
| Inventário completo | `CODEBASE.md` |
| Testes E2E engenharia | `e2e/run-e2e.mjs`, `e2e/README.md` |

---

*Documento normativo para o app `engenharia`. Alterações de padrão exigem atualização deste arquivo no mesmo PR.*
