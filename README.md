### Engenharia

Gestao de obras de engenharia civil

Especificacoes tecnicas: cadastro em **Technical Item** (parametros + formulas em **Technical Item Output**);
instancias na obra em **Project Item** (documento standalone ligado a **Construction Project**).

Testes: `bench --site <site> run-tests --app engenharia` (209+ testes)

**Painel de Obras:** zona de atenção + próximos compromissos (50/50), agenda operacional (sem pagamentos),
obras ativas em largura total, entradas×saídas do mês fixas, composição de custos por categoria,
filtros de linhas com atualização parcial (5/10/15).

**Custos de obra:** campo `funded_by` (Escritório vs Cliente) — custos pagos pelo cliente não entram no fluxo de caixa do escritório.

Documentação de usuário: `engenharia/docs/manual_usuario.md`

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench install-app engenharia
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/engenharia
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
