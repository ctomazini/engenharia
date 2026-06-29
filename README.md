# Engenharia

Gestão de obras de engenharia civil no **Frappe v16** (sem ERPNext). **Versão:** 1.3.0

Especificações técnicas: cadastro em **Technical Item** (parâmetros + fórmulas em **Technical Item Output**); instâncias na obra em **Project Item** (documento ligado a **Construction Project**).

---

## Documentação

| Documento | Conteúdo |
| --- | --- |
| [`CHANGELOG.md`](CHANGELOG.md) | Histórico de versões |
| [`engenharia/docs/README.md`](engenharia/docs/README.md) | Índice de toda a documentação |
| [`engenharia/docs/manual_usuario.md`](engenharia/docs/manual_usuario.md) | Manual do usuário (Desk) |
| [`engenharia/docs/desenvolvimento.md`](engenharia/docs/desenvolvimento.md) | Bench, testes, pre-commit, demo seed |
| [`e2e/README.md`](e2e/README.md) | Testes E2E Playwright |
| [`REGRAS_OBRIGATORIAS.md`](REGRAS_OBRIGATORIAS.md) | Padrões normativos do app |
| [`docs/audit-deploy-ready.md`](docs/audit-deploy-ready.md) | Auditoria deploy-ready |
| [`CODEBASE.md`](CODEBASE.md) | Inventário técnico (gerado) |
| [`docs/crosscheck_advocacia.md`](docs/crosscheck_advocacia.md) | Paridade com advocacia |
| [`docs/ux-final-executive-report.md`](docs/ux-final-executive-report.md) | Encerramento projeto UX |

---

## Destaques funcionais

- **Painel de Obras** (`/app/eng-dashboard`): atenção operacional, agenda, obras ativas, zona financeira (Manager) com **Orçado vs Realizado** e **Margem por Obra**, despesas pendentes, filtros com refresh parcial
- **Relatórios operacionais** (6 Script Reports): gráficos de barras, cards KPI, formatação colorida e **Print Formats** PDF (logo do escritório via Engineering Settings)
- **Despesas do Escritório** (`Office Expense`): custos de funcionamento com recorrência e integração no fluxo de caixa
- **Documentos Word**: geração a partir de modelos `.docx` com placeholders completos
- **Custos e subcontratos:** `funded_by` (Escritório vs Cliente)
- **Modelos de Etapas** (`Project Stage Template`)
- **Contratos:** parcelas com sync automático para **Payment**
- **API para agentes IA:** `engenharia/agent_api.py` — 4 endpoints read-only

---

## Testes

```bash
# Unitários / integração (320 testes)
bench --site engenharia.local run-tests --app engenharia

# E2E Playwright (ver e2e/README.md)
cd e2e && npm install && E2E_PASS=<senha> npm test
```

---

## Instalação

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench --site <site> install-app engenharia
bench --site <site> migrate
```

---

## Contribuição

```bash
cd apps/engenharia
pre-commit install
```

Ferramentas: ruff, eslint, prettier, pyupgrade. Commits em **Conventional Commits**.

---

## Licença

MIT

---

*Última atualização: 2026-06-29 22:20 UTC*
