# Changelog — app engenharia

Formato baseado em [Keep a Changelog](https://keepachangelog.com/). Versionamento [SemVer](https://semver.org/).

## [1.3.0] — 2026-06-29

### Added

- **Relatório de Recebimentos (Contador):** gerador de `.docx` via `docxtpl` com modos **Previsão** (vencimentos do mês) e **Realizado** (recebidos no mês), parcelas itemizadas e agrupadas por cliente com qualificação completa (CPF/CNPJ, endereço). Endpoint whitelisted `engenharia.receivables.get_monthly_receivables_report` (sem DocType novo, lookups em lote sem N+1).
- **Botão "Relatório para Contador"** na zona financeira do painel (`eng-dashboard`), restrito a Engenharia Manager, com diálogo de modo/mês/ano/modelo e download automático do `.docx`.
- Helper reutilizável `_render_docx_template` extraído de `_render_document` para renderização genérica de modelos `.docx`.

### Tests

- Suíte: **343** testes (11 novos em `tests/test_receivables.py`).

---

## [1.2.0] — 2026-06-29

### Added

- **Contrato principal:** campo `is_primary` em Engineering Contract (um por obra), com patch de backfill para obras de contrato único.
- **Seletor de contrato** no diálogo *Gerar Documentos* quando a obra tem mais de um contrato (padrão: contrato principal).
- **Resolução determinística de contrato** na geração: explícito → principal → fallback (prioridade de status + recência).
- **Formatação BR garantida** em todos os valores `_fmt` (milhar `.` e decimal `,`), independente do `number_format` do site.
- **Filtros/funções Jinja** de formatação BR em documentos: `real`/`moeda` e `num_br`/`numero` — permitem calcular com valores brutos e exibir formatado (ex.: `{{ (contract_base_value / project_construction_area) | real }}`).
- **Variantes `_fmt`** para `project_construction_area`, `project_physical_progress` e `project_default_bdi_percent`.
- **Botão "Como Usar os Placeholders"** no Modelo de Documento: janela com tutoriais e exemplos práticos (`get_placeholder_guide`).

### Changed

- Placeholders de contrato (`contract_*`) documentados como **um** contrato; `project_current_contract_value` esclarecido como **soma** dos contratos da obra.
- Download de documentos gerados com object URL mantido vivo + link clicável de fallback.

### Fixed

- Placeholders numéricos brutos saíam sem formatação BR; agora há variantes `_fmt` e filtros para cálculo formatado.

### Tests

- Suíte: **332** testes.

---

## [1.1.0] — 2026-06-23

### Added

- **Painel (Manager):** seções **Orçado vs Realizado** e **Margem por Obra** na zona financeira (`dashboard/budget_margin.py`, `budget_margin.js`).
- Batch `build_consolidated_costs_summary_batch` reutilizado nos reports e no painel (zero N+1).

### Changed

- **Modernização UX** (Etapas 01–09): glossário, sidebar, formulários, onboarding, empty states, ajuda contextual.
- **Script Reports:** chamadas explícitas por report em vez de monkey-patch global em `QueryReport.prototype`.
- **Performance:** limites de query e batch costs em `cash_flow`, `budget_vs_actual`, `project_margin`, `work_cost_by_*`.
- **Hub da obra:** layout de pills alinhado ao advocacia (desktop).

### Removed

- Relatório `projects_by_status` (Obras por Status) — visão substituída pelo painel e por filtros de status em Orçado vs Realizado.
- Helpers órfãos `donut_chart` e `PROJECT_STATUS_COLORS` em `report_visuals.py`.

### Tests

- Suíte: **320** testes (`319` + sidebar JSON).

---

## [1.0.0] — 2026-06-09

Release inicial deploy-ready: 46 DocTypes, 7 Script Reports (pré-remoção de Obras por Status), painel modular, hub da obra, Office Expense, print formats PDF, API agentes.

*Última atualização: 2026-06-23 23:24 UTC*
