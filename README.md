### Engenharia

Gestao de obras de engenharia civil

Especificacoes tecnicas: cadastro em **Technical Item** (parametros + formulas em **Technical Item Output**);
instancias na obra em **Project Item** (documento standalone ligado a **Construction Project**).

Testes: `bench --site <site> run-tests --app engenharia` (123 testes)

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
