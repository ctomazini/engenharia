# Changelog — app engenharia

Formato baseado em [Keep a Changelog](https://keepachangelog.com/). Versionamento [SemVer](https://semver.org/).

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
