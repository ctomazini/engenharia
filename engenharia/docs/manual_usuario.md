# Manual do Usuário — Módulo Engenharia

Sistema de gestão de obras de engenharia civil integrado ao Frappe/ERPNext Desk.

---

## 1. Visão Geral

### O que o sistema faz

O módulo **Engenharia** centraliza a operação de um escritório de projetos e obras:

- Cadastro de **clientes**, **fornecedores** e **obras**
- **Orçamento técnico** com itens, fórmulas e revisões
- **Contratos**, **parcelas** e **pagamentos**
- **Custos de obra**, **despesas reembolsáveis** e **comissões**
- **Prazos**, **tarefas**, **alvarás** e **medições**
- **Documentos** gerados a partir de modelos Word
- **Painel** com visão operacional e financeira

### Perfis de acesso

| Perfil | O que pode fazer |
|---|---|
| **Engenharia Manager** | Acesso completo: operacional + financeiro + configurações sensíveis (orçamento total da obra, comissões, contratos, pagamentos, custos) |
| **Engenharia User** | Operacional: projetos, etapas, itens técnicos da obra, prazos, tarefas, alvarás, medições, registros de horas e comunicações. **Não vê** contratos, pagamentos, comissões, custos nem a zona financeira do painel |

Se você tentar abrir um registro financeiro sem permissão, o sistema exibirá *Permissão insuficiente* — isso é esperado para o perfil User.

### Como acessar

1. Abra o navegador no endereço do site (ex.: `https://engenharia.local` ou URL da sua instalação).
2. Faça login com usuário e senha fornecidos pelo administrador.
3. No menu lateral, abra o workspace **Engenharia** ou a página **Painel de Obras**.

---

## 2. Painel Principal

O **Painel de Obras** reúne indicadores e atalhos do dia a dia.

### O que cada área mostra

| Área | Conteúdo |
|---|---|
| **Cabeçalho / Hero** | Data, período selecionado (7, 15 ou 30 dias), resumo de urgência |
| **Filtros** | Alterar janela de tempo e limites das listas |
| **Atenção imediata** | Tiles clicáveis: prazos críticos, tarefas atrasadas, protocolos (Manager também vê parcelas vencidas e custos pendentes) |
| **Agenda / Timeline** | Prazos, tarefas e (Manager) vencimentos financeiros no período |
| **Zona financeira** *(somente Manager)* | Saúde operacional, KPIs (a receber, vencido, custos do mês…), gráficos e listas de parcelas/despesas |

### Diferença Manager vs User

- **Manager** vê KPIs financeiros, gráficos de fluxo e listas de pagamentos.
- **User** vê apenas indicadores operacionais (prazos, tarefas, protocolos, horas). A seção financeira **não aparece** — não há mensagem de “acesso negado”, a área simplesmente não é exibida.

### Dicas

- Clique em um tile ou linha da agenda para ir direto à lista filtrada do registro correspondente.
- Use **↺ Atualizar** no canto superior para recarregar os dados.

---

## 3. Cadastros Básicos

Cadastros devem ser criados **antes** ou **conforme** a necessidade nas obras. Nomes em português abaixo são os **rótulos na tela**.

### 3.1 Clientes

**O que é:** pessoa física ou jurídica contratante das obras.

**Como criar:** Engenharia → Clientes → Novo.

**Campos importantes:**

- **Nome / Razão social** — identificação principal
- **CPF ou CNPJ** — validados automaticamente (apenas dígitos)
- **Contatos** e **Endereços** — tabelas na ficha do cliente

**Dica:** Um cliente pode ter várias obras vinculadas.

### 3.2 Fornecedores

**O que é:** empresas ou profissionais que prestam serviço ou vendem material.

**Campos:** Nome do fornecedor, CNPJ (opcional), categoria.

### 3.3 Tipos de Etapa

**O que é:** catálogo reutilizável de fases da obra (ex.: Fundação, Estrutura, Acabamento).

**Uso:** Ao criar **Etapas da Obra** no projeto, você escolhe um tipo de etapa. Pode incluir **percentual de avanço** padrão.

### 3.4 Tipos de Alvará

**O que é:** classificação de protocolos (Alvará de construção, Habite-se, ART/RRT, etc.).

### 3.5 Órgãos Públicos

**O que é:** prefeituras, órgãos ambientais, corpo de bombeiros — usados em **Prazos** e **Alvarás**.

### 3.6 Categorias de Custo

**O que é:** classificação de lançamentos de **Custo de Obra** (Material, Mão de obra, Equipamento…).

### 3.7 Itens Técnicos

**O que é:** catálogo de componentes de orçamento (ex.: Concreto usinado, Forma metálica).

Cada item pode ter:

- **Parâmetros** (entrada numérica, ex.: volume)
- **Saídas calculadas** (fórmulas, ex.: custo total = quantidade × preço unitário)
- **Unidade padrão**

**Dica:** Itens técnicos são reutilizados em várias obras via **Itens do Projeto**.

---

## 4. Projetos de Obra

**O que é:** registro central (hub) de cada obra — endereço, cliente, status, orçamento e links para tudo relacionado.

### Como criar

1. Engenharia → Projetos → Novo.
2. Selecione o **Cliente** (obrigatório).
3. Preencha tipo de obra, status inicial (geralmente **Orçamento**), endereço e datas previstas.

O sistema gera um código automático (ex.: `PROJ-2026-0042`) e um **título** com cliente e cidade.

### Campos importantes

| Campo (label) | Observação |
|---|---|
| Status | Orçamento → Em andamento → Concluída / Paralisada / Cancelada |
| Área construída | Metragem em m² |
| Avanço físico global | Calculado a partir das etapas |
| Orçamento / Revisão vigente | *(Manager)* controle de revisões de orçamento |
| Total especificações | *(Manager)* soma automática dos itens do projeto |

**Engenharia User** não vê a seção de orçamento nem totais financeiros agregados no projeto.

### Etapas da Obra

Crie registros **Etapa da Obra** vinculados ao projeto, escolhendo **Tipo de etapa** e informando avanço e datas.

### Itens do Projeto

São as linhas de orçamento/especificação técnica da obra:

1. Escolha um **Item técnico** do catálogo.
2. Informe **quantidade** e parâmetros.
3. O sistema calcula **custos** e **valor total** conforme fórmulas do item técnico.

**Lógica automática:** sempre que um item é salvo ou removido, o **total de especificações da obra** é recalculado *(visível ao Manager)*.

### Aba Conexões

No projeto, use a aba **Conexões** para abrir contratos, pagamentos, custos, comissões, prazos, tarefas, etc. *(links financeiros só funcionam para Manager)*.

---

## 5. Contratos

**O que é:** acordo de honorários/serviços vinculado a uma obra.

### Criar contrato

1. Abra a obra ou vá em Engenharia → Contratos → Novo.
2. Selecione a **Obra** — o **Cliente** é preenchido automaticamente.
3. Informe valores e status **Vigente**.

### Parcelas

Na tabela **Parcelas**, defina datas de vencimento e valores. Ao salvar o contrato, o sistema **gera ou atualiza** registros de **Pagamento** correspondentes.

### Aditivos

Registre alterações contratuais na tabela de **Aditivos**. Use o botão **Aplicar aditivo** para:

- Regerar parcelas futuras (preservando as já recebidas), ou
- Apenas registrar histórico

### Acompanhamento

- **Pagamentos** mostram status: Pendente, Vencido, Recebido.
- O valor **atual do contrato** considera aditivos aprovados.

*(Disponível apenas para Engenharia Manager.)*

---

## 6. Financeiro

### 6.1 Pagamentos

Recebíveis de contrato e fluxos derivados. Cada parcela gera um pagamento rastreável.

**Status comuns:** Pendente, Vencido, Recebido, Cancelado.

No painel, o Manager pode marcar pagamento como recebido (atalho na lista).

### 6.2 Custos de Obra

Lançamento de despesas da obra por **categoria**, **fornecedor** e **etapa**.

Use para relatórios de margem e custo por categoria.

### 6.3 Despesas Reembolsáveis

Despesas pagas pelo escritório que o **cliente deve devolver**. Fluxo separado dos custos de obra.

Status típico: **A reembolsar** → reembolsado via pagamento vinculado.

### 6.4 Comissões

Registro de comissões a receber (ex.: pré-moldado, parceiro).

1. Crie **Comissão** vinculada à **Obra**.
2. Informe fornecedor, valor total e tipo.
3. Registre **pagamentos recebidos** na tabela inferior (com data, valor e opcionalmente **comprovante** anexo).
4. O sistema calcula **Total pago**, **Saldo a receber** e status (Aberta / Parcial / Paga).
5. O campo **Comissões a receber** na obra agrega todas as comissões abertas *(Manager)*.

---

## 7. Medições

**O que é:** registro de medição de serviços executados em campo, vinculado à obra.

### Como registrar

1. Engenharia → Medições → Novo.
2. Selecione a **Obra** e o **Período de referência**.
3. Na tabela de **Itens**, informe etapas e quantidades medidas.

Útil para conferência de avanço físico e faturamento por medição.

---

## 8. Prazos e Tarefas

### 8.1 Prazos

**O que é:** compromissos com data limite — especialmente relacionados a **órgãos públicos** (protocolos, licenças) ou obrigações contratuais.

**Campos:** Obra, descrição, data de vencimento, status, órgão (quando aplicável).

**Calendário:** ao salvar, um evento aparece no **Calendário** do Frappe. Se o administrador configurou **Google Calendar**, o evento pode sincronizar.

### 8.2 Tarefas

**O que é:** ações internas da equipe (ligar cliente, revisar projeto, visita técnica).

**Campos:** Assunto, obra, responsável, prioridade, data limite, status (A fazer / Fazendo / Concluída).

**Timer:** use o registro de **Horas** ou o timer global para cronometrar atividades.

### Diferença conceitual

| | Prazo | Tarefa |
|---|---|---|
| Foco | Externo / compliance / órgão | Interno / equipe |
| Exemplo | Vencimento alvará | Revisar memorial descritivo |
| Calendário automático | Sim (Event) | Não (por padrão) |

---

## 9. Alvarás e Protocolos

**O que é:** controle de protocolos em prefeituras e órgãos (número, data, validade, status).

Vincule **Tipo de alvará**, **Órgão público** e **Obra**.

Status incluem deferido, indeferido, cancelado — eventos de calendário são atualizados automaticamente.

---

## 10. Documentos

### 10.1 Modelos de Documento

Cadastre modelos Word (.docx) com **placeholders** (ex.: `{customer_name}`, `{project_address}`).

Tipos: contrato, proposta, memorial, etc.

### 10.2 Kits de Documentos

Agrupe vários modelos em um **Kit** para gerar pacotes completos de uma vez.

### 10.3 Gerar documento

Na **Obra**, use o botão de geração de documentos (ou menu Documentos):

1. Escolha o modelo.
2. O sistema preenche placeholders com dados da obra, cliente, especificações e contrato.
3. Baixe o `.docx` gerado ou anexe à obra.

Configure **CNPJ do escritório** em **Configurações da Engenharia** para aparecer nos documentos.

---

## 11. Registro de Atividades

### 11.1 Registro de Horas

Controle tempo gasto por **atividade** e **obra**.

- Crie manualmente informando duração, ou
- Use **Iniciar timer** / **Parar timer** ( também disponível globalmente na barra do sistema).

### 11.2 Registro de Comunicação

Histórico de ligações, e-mails e reuniões com clientes ou órgãos.

Informe **Assunto**, obra, tipo de comunicação e resumo.

---

## 12. Configurações

**Configurações da Engenharia** (registro único):

- Dados do escritório (CNPJ, razão social)
- Parâmetros globais usados em documentos e relatórios

*(Acesso tipicamente restrito ao Manager.)*

---

## 13. Dicas e Atalhos

### Busca rápida

- **Ctrl+K** (ou ícone de lupa): busca global por clientes, obras, contratos, etc.
- Digite parte do **título** visível (ex.: nome do cliente) — não é necessário memorizar códigos internos.

### Filtros em listas

- Use filtros de **Status**, **Cliente** ou **Obra** nas colunas.
- Listas de pagamentos e prazos têm **indicadores coloridos** (verde/laranja/vermelho).

### Workspace e favoritos

- Fixe o workspace **Engenharia** no menu.
- Marque registros com estrela para acesso rápido.

### Importação

Clientes, fornecedores, obras e órgãos públicos suportam **importação CSV** (menu Importar na lista).

### O que o perfil User **não** vê

Contratos, pagamentos, custos, despesas reembolsáveis, comissões, totais de orçamento na obra e toda a zona financeira do painel. Para essas funções, solicite perfil **Engenharia Manager** ao administrador.

---

*Manual versão 1.0 — junho/2026. Alinhado ao app engenharia no Frappe v16.*
