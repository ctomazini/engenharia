# Modernização UX - App Engenharia

Documento permanente de acompanhamento do projeto de modernização de experiência do usuário.

**Criado:** 2026-06-05  
**Última atualização:** 2026-06-05 (Etapa 02 concluída)  
**App:** `engenharia` (Frappe v16)

---

## Objetivos

* Simplificar a experiência do usuário
* Aplicar o Glossário Oficial Sprint 1A
* Reduzir complexidade percebida
* Melhorar navegação
* Preservar compatibilidade total com o banco de dados

---

## Restrições

Nunca:

* Renomear DocTypes EN
* Renomear Roles
* Renomear Slugs de Relatórios
* Renomear Rotas
* Renomear Placeholders Word
* Alterar Schema
* Alterar Child Tables
* Alterar Dados de Produção

---

## Glossário Oficial

**Status:** Sprint 1A — definido, não implementado no código.

### Princípios

1. **Singular** = registro / DocType / formulário. **Plural** = lista, menu, seção quando fizer sentido gramatical.
2. **Recebimentos** = dinheiro **a receber do cliente** (`Payment`). **Pagamentos efetuados** = dinheiro **pago** (compras, subcontratos, comissões recebidas, etc.) — termos distintos, não intercambiáveis.
3. **Orçamento** = planejado (`Project Item`). **Custos realizados** = fato (`Work Cost` + `Subcontract` + `Reimbursable Expense`).
4. Nome interno Frappe (coluna “Conceito técnico”) **permanece inalterado** até decisão explícita fora deste projeto.

### 1. App, módulo e painel

| Conceito | Nome técnico | Nome oficial |
|----------|--------------|--------------|
| Aplicativo | `engenharia` | Engenharia |
| Módulo / workspace | `Engenharia` | Engenharia |
| Painel principal | `eng-dashboard` | Painel de Obras |
| Atalho no menu | — | Painel |

### 2. Seções do menu lateral

| Conceito | Nome oficial |
|----------|--------------|
| Seção operacional diária | Dia a Dia |
| Seção hub da obra | Obras |
| Seção planejamento técnico-financeiro | Orçamento |
| Seção honorários e entradas | Receitas |
| Seção saídas e compromissos | Despesas |
| Seção analytics | Relatórios |
| Seção cadastros mestre | Cadastros |
| Seção admin | Administração |

### 3. DocTypes — transacionais e operacionais

| Conceito | Nome técnico | Nome oficial (registro) | Nome oficial (lista / menu) |
|----------|--------------|-------------------------|----------------------------|
| Obra (hub) | `Construction Project` | Obra | Obras |
| Cliente | `Customer` | Cliente | Clientes |
| Contrato de honorários | `Engineering Contract` | Contrato de Honorários | Contratos de Honorários |
| Recebível de honorários | `Payment` | Recebimento | Recebimentos |
| Compra / NF pontual | `Work Cost` | Compra ou NF Avulsa | Compras e NF Avulsas |
| Contrato com prestador | `Subcontract` | Subcontrato | Subcontratos |
| Despesa paga pelo escritório a reembolsar | `Reimbursable Expense` | Despesa Reembolsável | Despesas Reembolsáveis |
| Despesa de funcionamento | `Office Expense` | Despesa do Escritório | Despesas do Escritório |
| Comissão a receber | `Commission` | Comissão | Comissões |
| Prazo / compliance | `Deadline` | Prazo | Prazos |
| Tarefa interna | `Task` | Tarefa | Tarefas |
| Alvará / protocolo em órgão | `Permit` | Alvará e Protocolo | Alvarás e Protocolos |
| Medição de campo | `Construction Measurement` | Boletim de Medição | Boletins de Medição |
| Comunicação registrada | `Communication Log` | Comunicação | Comunicações |
| Horas trabalhadas | `Time Log` | Registro de Horas | Registro de Horas |
| Documento anexo / gerado | `Project Document` | Documento da Obra | Documentos da Obra |
| Linha de orçamento da obra | `Project Item` | Item do Orçamento | Itens do Orçamento |
| Etapa executiva | `Project Stage` | Etapa da Obra | Etapas |
| Configuração single | `Engineering Settings` | Configurações do Escritório | Configurações do Escritório |

### 4. DocTypes — cadastros auxiliares

| Conceito | Nome técnico | Nome oficial (registro) | Nome oficial (lista / menu) |
|----------|--------------|-------------------------|----------------------------|
| Item reutilizável de catálogo | `Technical Item` | Catálogo Técnico | Catálogo Técnico |
| Fornecedor / prestador | `Supplier` | Fornecedor | Fornecedores |
| Classificação de despesa | `Cost Category` | Classificação de Gasto | Classificações de Gasto |
| Tipo de edificação | `Building Type` | Tipo de Edificação | Tipos de Edificação |
| Categoria de arquivo | `Document Category` | Categoria de Documento | Categorias de Documento |
| Tipo de fase da obra | `Stage Type` | Tipo de Etapa | Tipos de Etapa |
| Prefeitura / órgão | `Public Agency` | Órgão Público | Órgãos Públicos |
| Classificação de alvará/protocolo | `Permit Type` | Tipo de Alvará e Protocolo | Tipos de Alvará e Protocolo |
| Modelo Word | `Document Template` | Template de Documento | Templates de Documento |
| Pacote de modelos | `Document Kit` | Kit de Documentos | Kits de Documentos |
| Template de fases | `Project Stage Template` | Modelo de Etapas | Modelos de Etapas |

### 5. Child tables (registros filhos)

| Conceito | Nome técnico | Nome oficial |
|----------|--------------|--------------|
| Parcela do contrato | `Engineering Contract Installment` | Parcela do Contrato |
| Aditivo contratual | `Engineering Contract Amendment` | Aditivo Contratual |
| Parcela paga (compra avulsa) | `Work Cost Payment` | Pagamento Efetuado |
| Parcela paga (subcontrato) | `Subcontract Payment` | Pagamento Efetuado |
| Reembolso recebido | `Reimbursable Expense Reimbursement` | Reembolso Recebido |
| Pagamento ao fornecedor (reembolsável) | `Reimbursable Expense Payment` | Pagamento ao Fornecedor |
| Recebimento de comissão | `Commission Payment` | Recebimento de Comissão |
| Linha do boletim | `Construction Measurement Item` | Item do Boletim |
| Contato do cliente | `Customer Contact` | Contato do Cliente |
| Endereço do cliente | `Customer Address` | Endereço do Cliente |
| Item do kit | `Document Kit Item` | Item do Kit |
| Parâmetro de item | `Project Item Parameter` | Parâmetro do Item |
| Resultado calculado (item) | `Project Item Output` | Resultado do Item |
| Componente de custo (item) | `Project Item Cost Component` | Componente de Custo |
| Campo do catálogo | `Technical Item Field` | Campo Técnico |
| Resultado do catálogo | `Technical Item Output` | Resultado Técnico |
| Revisão de orçamento | `Project Budget Revision` | Revisão de Orçamento |
| Especificação legada (child) | `Project Specification` | Especificação da Obra |
| Item do modelo de etapas | `Project Stage Template Item` | Item do Modelo de Etapas |

### 6. Relatórios

| Conceito | Slug (técnico) | Nome oficial |
|----------|----------------|--------------|
| Custos realizados consolidados | `consolidated_cost` | Custos Realizados |
| Orçamento × fato | `budget_vs_actual` | Orçado vs Realizado |
| Compras avulsas por obra | `work_cost_by_project` | Compras Avulsas por Obra |
| Compras avulsas por categoria | `work_cost_by_category` | Compras Avulsas por Categoria |
| Fluxo de caixa | `cash_flow` | Fluxo de Caixa |
| Margem | `project_margin` | Margem por Obra |
| Distribuição por status | `projects_by_status` | Obras por Status |

**Nota:** um único nome oficial por relatório. O atalho duplicado “Visão de Custos Realizados” será eliminado na implementação; nome canônico: **Custos Realizados**.

### 7. Abas e painéis dentro da Obra

| Conceito | Nome oficial |
|----------|--------------|
| Área de orçamento / especificações na obra | Orçamento da Obra |
| Tabela de linhas de orçamento (na obra) | Itens do Orçamento |
| Prévia / total do orçamento | Total do Orçamento |
| Área financeira resumida | Financeiro |
| Parcelas de honorários (visão na obra) | Recebimentos |
| Despesas de obra pagas/comprometidas | Custos Realizados |
| Pagamentos registrados na obra (saídas) | Pagamentos Efetuados |
| Despesas a reembolsar | Despesas Reembolsáveis |
| Comissões vinculadas | Comissões |
| Prazos | Prazos |
| Alvarás e protocolos | Alvarás e Protocolos |
| Tarefas | Tarefas |
| Comunicações | Comunicações |
| Medições | Medições |
| Horas | Horas Trabalhadas |
| Arquivos Word/PDF | Documentos da Obra |
| Avanço por fase | Etapas da Obra |

### 8. Conceitos de domínio (não são DocTypes)

| Conceito | Nome oficial | Não confundir com |
|----------|--------------|-------------------|
| Valor planejado da obra | Orçamento | Custos Realizados |
| Valor efetivamente pago/comprometido na obra | Custos Realizados | Orçamento |
| Entrada de honorários do cliente | Recebimentos | Pagamentos Efetuados |
| Saída paga a fornecedor/prestador | Pagamento Efetuado | Recebimento |
| Quem paga a despesa | Quem Arca (Escritório / Cliente) | — |
| Condição da parcela (contrato) | Condição de Pagamento | Vencimento |
| Revisão formal do orçamento | Revisão de Orçamento | Aditivo Contratual |
| Alteração contratual de valor | Aditivo Contratual | Revisão de Orçamento |

### 9. Perfis, fixtures e outros nomes visíveis

| Conceito | Nome técnico | Nome oficial (UI) |
|----------|--------------|-------------------|
| Perfil operacional | `Engenharia User` | Usuário Engenharia |
| Perfil gestor | `Engenharia Manager` | Gestor Engenharia |
| Kanban de tarefas | `Engenharia Obras` | Tarefas da Obra |
| Notificação prazo | `Engenharia - Prazo vencendo` | Prazo vencendo |
| Notificação parcela | `Engenharia - Parcela vencida` | Parcela vencida |
| Notificação alvará | `Engenharia - Protocolo expirando` | Alvará ou protocolo expirando |
| Notificação tarefa | `Engenharia - Tarefa atrasada` | Tarefa atrasada |

### 10. Fora do glossário UI (intocáveis neste projeto)

| Elemento | Regra |
|----------|--------|
| DocType `name` EN | Permanece (ex.: `Payment`, `Construction Project`) |
| Slugs de relatório | Permanecem (ex.: `consolidated_cost`) |
| Rota do painel | Permanece `eng-dashboard` |
| Placeholders Word | Permanecem em inglês (`customer_name`, etc.) |
| Custom fields Event | Permanecem `custom_source_*` (hidden) |

### Unificação de divergências (Sprint 1A)

| Antes (coexistia) | Nome oficial Sprint 1A |
|-------------------|------------------------|
| Pagamentos / Recebimento / Recebimentos (`Payment`) | Recebimentos (lista) · Recebimento (registro) |
| Itens do Projeto / Item do Orçamento / Especificações | Item do Orçamento · aba Orçamento da Obra |
| Itens Técnicos / Catálogo Técnico | Catálogo Técnico |
| Protocolos / Protocolo / Alvarás | Alvará e Protocolo · Alvarás e Protocolos |
| Configurações / Configurações do Escritório | Configurações do Escritório |
| Visão de Custos Realizados / Custos Realizados | Custos Realizados |
| `cash_flow` / `project_margin` (título EN na UI) | Fluxo de Caixa · Margem por Obra |
| Projetos (manual) | Obras |

---

## Registro de Etapas

### Etapa 01 — Descoberta, auditorias e glossário

**Status:** Concluída (somente análise e documentação; zero alteração de código UX)

**Data:** 2026-06-05

**Responsável:** Sessão Agent / projeto Engenharia

**Objetivo:**

* Auditar UX sob perspectiva de usuário leigo
* Auditar inventário técnico completo (workspaces, DocTypes, reports, scripts, permissões, traduções)
* Produzir matriz de impacto para mudanças de nomenclatura
* Definir Glossário Oficial Sprint 1A
* Criar este documento de acompanhamento permanente

**Arquivos analisados:**

* `engenharia/setup/sidebar.py`, `engenharia/workspace_sidebar/engenharia.json`
* `engenharia/engenharia/workspace/engenharia/engenharia.json`
* `engenharia/setup/translations.py`, `engenharia/setup/permissions.py`
* `engenharia/hooks.py`, `engenharia/setup/reports.py`, `engenharia/setup/print_formats.py`
* `engenharia/engenharia/doctype/**` (49 DocTypes)
* `engenharia/engenharia/report/**` (7 reports)
* `engenharia/public/js/hub.js`, `eng_hub_nav.js`, `public/js/dashboard/*`, `reports_common.js`
* `engenharia/docs/manual_usuario.md`, `engenharia/docs/audit_usability.md`
* `CODEBASE.md`

**Mudanças realizadas:**

* Nenhuma alteração de código, schema, banco ou configuração de produção
* Criação deste arquivo `docs/ux-modernization-roadmap.md`

**Arquivos modificados:**

* `docs/ux-modernization-roadmap.md` (novo)

**Impactos identificados:**

* Nota UX leigo ~5/10; principal fricção: volume de menus, nomenclatura duplicada, orçamento técnico denso
* Sidebar JSON desatualizado (37 vs 40 links canônicos em `sidebar.py`)
* Inconsistência Pagamentos vs Recebimentos para o mesmo DocType `Payment`
* Três relatórios com `report_name` em inglês na UI
* Relatório `consolidated_cost` duplicado no menu com rótulos diferentes
* `Engenharia User` com role em reports financeiros mas sem read nos DocTypes financeiros

**Riscos identificados:**

* Renomear DocType EN, slugs ou rotas = risco crítico
* Unificar “Pagamentos” cegamente pode confundir recebíveis com pagamentos efetuados (Work Cost/Subcontract)
* Alterar placeholders Word quebra templates `.docx` existentes

**Testes executados:**

* Nenhum (etapa somente leitura)

**Resultado:**

* Base normativa pronta para Sprint 1B+ (implementação cosmética alinhada ao glossário)
* Matriz de impacto documentada na conversa (M1–M18); referência cruzada nas decisões DEC-001–DEC-008

**Pendências:**

* Implementar glossário no código (translations, sidebar, workspace, labels JSON, JS `__()`)
* Sync `workspace_sidebar/engenharia.json` com `sidebar.py`
* Atualizar `manual_usuario.md` após implementação
* Decidir ordem de sprints de implementação (M6 → M8/M2/M10 → M1/M5…)

**Próximas etapas:**

* **Etapa 02:** Sync estrutural `workspace_sidebar/engenharia.json` com `sidebar.py` (sem alteração de labels)
* **Etapa 03:** Labels workspace, hub, construction_project JSON + traduções conforme glossário
* **Etapa 04:** `report_name` PT + deduplicação menu Custos Realizados
* **Etapa 05:** Manual e checklist pós-migrate

---

### Etapa 02 — Sync estrutural da sidebar (sem nomenclatura)

**Status:** Concluída

**Data:** 2026-06-05

**Responsável:** Sessão Agent / projeto Engenharia

**Branch:** `ux/step-02-sidebar-sync`

**Objetivo:**

* Eliminar drift estrutural entre `sidebar.py` (fonte canônica) e `workspace_sidebar/engenharia.json`
* Restaurar links ausentes sem alterar rótulos visíveis, traduções, dashboards ou formulários
* Garantir que `_validate_sidebar_links()` deixe de registrar erro de contagem no migrate

**Arquivos analisados:**

* `engenharia/setup/sidebar.py` — `SIDEBAR_LINK_ORDER` (40 links)
* `engenharia/workspace_sidebar/engenharia.json` — estava com 37 links
* `engenharia/engenharia/workspace/engenharia/engenharia.json` — atalhos e rotas válidas (sem alteração)
* `engenharia/desktop_icon/engenharia.json` — referência válida a Workspace Sidebar

**Plano de correção (aprovado):**

| # | Divergência | Ação | Escopo |
|---|-------------|------|--------|
| 1 | JSON sem `Project Document` após `Permit` | Inserir link `Documentos da Obra` | Estrutural |
| 2 | JSON sem `Building Type` e `Document Category` em Cadastros | Inserir após `Cost Category` | Estrutural |
| 3 | Validação migrate falha 37≠40 | Teste de paridade JSON↔Python | Prevenção |
| — | Labels (Protocolos, Visão de Custos, Pagamentos workspace) | **Não alterar** nesta etapa | Etapa 03+ |
| — | Traduções / glossário | **Não alterar** nesta etapa | Etapa 03+ |

**Mudanças realizadas:**

* Adicionados 3 links ao `workspace_sidebar/engenharia.json` na ordem de `SIDEBAR_LINK_ORDER`
* Criado `engenharia/tests/test_sidebar_json.py` — paridade label/`link_to`/`link_type` sem depender do banco
* Nenhuma alteração de label, tradução, workspace shortcuts, hub, dashboard ou DocType JSON

**Arquivos modificados:**

* `engenharia/workspace_sidebar/engenharia.json`
* `engenharia/tests/test_sidebar_json.py` (novo)
* `docs/ux-modernization-roadmap.md`

**Impactos identificados:**

* DIV-002 resolvida estruturalmente (40 links alinhados)
* Após `bench migrate`, sidebar no site passa a exibir Documentos da Obra, Tipos de Edificação e Categorias de Documento
* DIV-001, DIV-003–DIV-008 permanecem para etapas de nomenclatura

**Riscos identificados:**

* Baixo: apenas import de fixture JSON no migrate; ícones escolhidos (`file-archive`, `home`, `bookmark`) seguem padrão Lucide do desk

**Testes executados:**

* `bench --site engenharia.local run-tests --app engenharia` — 321 testes OK
* `engenharia.tests.test_sidebar_json` — paridade 40/40 OK

**Resultado:**

* Fonte canônica Python e JSON sincronizadas; regressão bloqueada por teste unitário
* Nomenclatura e UX cosmética intactas (escopo Etapa 03+)

**Pendências:**

* Etapa 03: labels e traduções conforme glossário Sprint 1A
* Etapa 04: `report_name` PT + deduplicação menu Custos Realizados
* Etapa 05: manual e checklist pós-migrate

**Próximas etapas:**

* **Etapa 03:** Aplicar glossário em labels (workspace, hub, translations) — risco verde

**Commits:**

| Hash | Mensagem |
|------|----------|
| *(ver git log na branch)* | `[UX-STEP-01] Docs: add ux modernization roadmap` |
| *(ver git log na branch)* | `[UX-STEP-02] Fix: synchronize workspace_sidebar.json with sidebar.py` |
| *(ver git log na branch)* | `[UX-STEP-02] Test: add sidebar link order parity test` |
| *(ver git log na branch)* | `[UX-STEP-02] Docs: update modernization roadmap` |

---

### Etapa 03

**Status:** Pendente

**Data:**

**Responsável:**

**Objetivo:**

**Arquivos analisados:**

**Mudanças realizadas:**

**Arquivos modificados:**

**Impactos identificados:**

**Riscos identificados:**

**Testes executados:**

**Resultado:**

**Pendências:**

**Próximas etapas:**

---

## Decisões Arquiteturais

### DEC-001

**Contexto:** Múltiplos rótulos para `Payment` (Pagamentos, Recebimento, Recebimentos).

**Decisão:** Nome oficial **Recebimentos** (lista) e **Recebimento** (registro). Manter **Pagamentos Efetuados** exclusivamente para saídas (Work Cost, Subcontract, etc.).

**Motivação:** Evitar ambiguidade financeira; alinhado à expectativa do usuário leigo.

**Impacto:** `translations.py`, workspace, hub, abas da Obra, dashboard quick_actions — sem alterar `Payment` EN.

---

### DEC-002

**Contexto:** `Permit` traduzido como “Protocolo”; manual e usuários falam “Alvará”.

**Decisão:** Nome oficial **Alvará e Protocolo** (registro) / **Alvarás e Protocolos** (lista).

**Motivação:** Cobrir habite-se, alvará de construção e protocolos administrativos num único termo.

**Impacto:** `translations.py`, sidebar, hub, `Permit Type` → Tipo de Alvará e Protocolo.

---

### DEC-003

**Contexto:** Três camadas de nomenclatura para orçamento (Itens do Projeto, Item do Orçamento, Especificações).

**Decisão:** DocType/lista **Item do Orçamento** / **Itens do Orçamento**; aba na Obra **Orçamento da Obra**.

**Motivação:** Separar claramente planejamento (orçamento) de custos realizados.

**Impacto:** sidebar, construction_project JSON labels, hub, manual.

---

### DEC-004

**Contexto:** `Technical Item` como “Itens Técnicos” no menu vs “Catálogo Técnico” na tradução.

**Decisão:** Nome oficial único **Catálogo Técnico**.

**Motivação:** Deixa claro que é cadastro mestre reutilizável, não linha da obra.

**Impacto:** sidebar, mensagens JS, manual.

---

### DEC-005

**Contexto:** Restrições de modernização UX vs integridade do sistema.

**Decisão:** Sprint UX limita-se a labels, traduções, menus, textos de ajuda e organização visual. Proibido renomear DocTypes EN, slugs, rotas, roles, placeholders, schema.

**Motivação:** Matriz de impacto identificou risco crítico em renomeações estruturais.

**Impacto:** Define o escopo de todas as etapas futuras.

---

### DEC-006

**Contexto:** `workspace_sidebar/engenharia.json` com 37 links; `sidebar.py` define 40.

**Decisão:** Fonte canônica de ordem e labels = `SIDEBAR_LINK_ORDER` em `sidebar.py`; JSON deve ser sincronizado na Etapa 02.

**Motivação:** Validação `_validate_sidebar_links` já detecta drift; links ausentes prejudicam UX.

**Impacto:** Adicionar Documentos da Obra, Tipos de Edificação, Categorias de Documento ao JSON.

---

### DEC-007

**Contexto:** Dois links sidebar para o mesmo report `consolidated_cost`.

**Decisão:** Eliminar rótulo “Visão de Custos Realizados”; manter apenas **Custos Realizados**.

**Motivação:** Reduzir redundância percebida (auditoria UX).

**Impacto:** `sidebar.py`, `workspace_sidebar.json` — slug inalterado.

---

### DEC-008

**Contexto:** Relatórios `cash_flow`, `project_margin`, `projects_by_status` com `report_name` EN.

**Decisão:** Alterar apenas campo `report_name` para PT oficial; slugs permanecem.

**Motivação:** Baixo risco (M8 na matriz de impacto).

**Impacto:** 3 JSONs em `engenharia/report/` + migrate via `setup/reports.py`.

---

## Divergências Encontradas

| ID | Divergência | Onde | Resolução prevista |
|----|-------------|------|-------------------|
| DIV-001 | Pagamentos vs Recebimentos (`Payment`) | workspace, hub, translations | DEC-001 / glossário |
| DIV-002 | Sidebar JSON 37 ≠ Python 40 links | `workspace_sidebar.json` vs `sidebar.py` | **Resolvido Etapa 02** (estrutural) |
| DIV-003 | Itens do Projeto vs Item do Orçamento | sidebar vs translations | DEC-003 |
| DIV-004 | Itens Técnicos vs Catálogo Técnico | sidebar vs translations | DEC-004 |
| DIV-005 | Protocolos vs Alvarás e Protocolos | sidebar vs aba obra vs translations | DEC-002 |
| DIV-006 | Configurações vs Configurações do Escritório | translations vs sidebar | Glossário §3 |
| DIV-007 | consolidated_cost duplicado no menu | sidebar Despesas + Relatórios | DEC-007 |
| DIV-008 | report_name EN (3 relatórios) | `report/*.json` | DEC-008 |
| DIV-009 | Manual “Projetos” vs UI “Obras” | `manual_usuario.md` | Etapa 05 |
| DIV-010 | Engenharia User em reports financeiros sem DocPerm | `report/*.json` vs `permissions.py` | Débito UX-003 (fora Sprint 1 cosmético) |
| DIV-011 | Kanban `Engenharia Obras` referencia `Task` | fixture | Glossário: renomear label UI para Tarefas da Obra (etapa futura) |

---

## Débitos Técnicos Identificados

| ID | Débito | Severidade | Etapa sugerida |
|----|--------|------------|----------------|
| UX-DT-001 | Task / Project Stage sem `*_list.js` customizado | Baixa | Pós-Sprint 1 |
| UX-DT-002 | Project Item — curva de aprendizado alta (fórmulas) | Média | Sprint UX conteúdo/ajuda |
| UX-DT-003 | Reports financeiros acessíveis a Engenharia User sem read nos DocTypes | Média | Sprint permissões |
| UX-DT-004 | Perfil User oculta financeiro sem mensagem explicativa | Média | Sprint UX onboarding |
| UX-DT-005 | Placeholders Word em inglês — barreira para autor de templates | Baixa | Documentação apenas |
| UX-DT-006 | `Project Specification` child em FINANCIAL_DOCTYPES | Baixa | Revisão permissions.py |

---

## Mudanças Rejeitadas

### Renomear DocType `Payment` → `Receipt` (ou equivalente PT)

**Motivo da rejeição:** Risco crítico na Matriz de Impacto (M13). Quebra `financial.py`, hooks, permissions, testes e dados em `tabPayment`.

---

### Renomear slug `eng-dashboard`

**Motivo da rejeição:** Risco crítico (M11). Quebra bookmarks, e2e, breadcrumbs, 13 módulos dashboard.

---

### Renomear slugs de relatório (ex.: `cash_flow` → `fluxo_caixa`)

**Motivo da rejeição:** Risco crítico (M9). Quebra print formats, `reports_common.js`, bookmarks e registros `Report` no banco.

---

### Traduzir placeholders Word (`customer_name` → PT)

**Motivo da rejeição:** Risco crítico (M16). Invalida todos os templates `.docx` em produção.

---

### Renomear Roles `Engenharia User` / `Engenharia Manager`

**Motivo da rejeição:** Risco crítico (M17). Impacta permissions, reports, fixtures, usuários atribuídos.

---

### Unificar “Pagamentos” em Work Cost / Subcontract com “Recebimentos”

**Motivo da rejeição:** Conceitos de domínio distintos (entrada vs saída). Glossário mantém **Pagamento Efetuado** para despesas.

---

## Checklist de Segurança

Validar continuamente:

* [x] Nenhum DocType EN alterado (Etapa 01)
* [x] Nenhum Role alterado (Etapa 01)
* [x] Nenhum Report Slug alterado (Etapa 01)
* [x] Nenhuma rota alterada (Etapa 01)
* [x] Nenhum placeholder Word alterado (Etapa 01)
* [x] Nenhum schema alterado (Etapa 01)
* [x] Sidebar JSON sincronizado com `SIDEBAR_LINK_ORDER` (Etapa 02)
* [x] Nenhum label de UX alterado na Etapa 02

---

*Atualizar este documento ao final de cada etapa antes de encerrar os trabalhos.*
