# Engenharia

Gestão de obras de engenharia civil no **Frappe v16** (sem ERPNext).

Especificações técnicas: cadastro em **Technical Item** (parâmetros + fórmulas em **Technical Item Output**); instâncias na obra em **Project Item** (documento ligado a **Construction Project**).

---

## Documentação

| Documento | Conteúdo |
| --- | --- |
| [`engenharia/docs/README.md`](engenharia/docs/README.md) | Índice de toda a documentação |
| [`engenharia/docs/manual_usuario.md`](engenharia/docs/manual_usuario.md) | Manual do usuário (Desk) |
| [`engenharia/docs/desenvolvimento.md`](engenharia/docs/desenvolvimento.md) | Bench, testes, pre-commit, demo seed |
| [`e2e/README.md`](e2e/README.md) | Testes E2E Playwright |
| [`REGRAS_OBRIGATORIAS.md`](REGRAS_OBRIGATORIAS.md) | Padrões normativos do app |
| [`docs/audit-deploy-ready.md`](docs/audit-deploy-ready.md) | Auditoria deploy-ready (2026-06-07) |

---

## Destaques funcionais

- **Painel de Obras** (`/app/eng-dashboard`): atenção operacional, agenda, obras ativas, zona financeira (Manager), filtros com refresh parcial
- **Relatórios operacionais** (5 Script Reports): gráficos de barras/donut, cards KPI e formatação colorida nas tabelas
- **Documentos Word**: geração a partir de modelos `.docx` com placeholders completos (obra, orçamento, contrato, subcontratos)
- **Custos e subcontratos:** `funded_by` (Escritório vs Cliente) — lançamentos pagos pelo cliente não entram no caixa do escritório
- **Contratos:** parcelas com sync automático para **Payment**

---

## Testes

```bash
# Unitários / integração (211 testes)
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
