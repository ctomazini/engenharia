"""Aplica description em campos de DocType JSON (uso único / manutenção)."""

from __future__ import annotations

import json
from pathlib import Path

SKIP_FIELDTYPES = frozenset({"Section Break", "Column Break", "Tab Break", "HTML", "Button"})

DESCRIPTIONS: dict[str, dict[str, str]] = {
	"Construction Project": {
		"customer": "Cliente contratante desta obra.",
		"title": "Título automático no formato ID — cliente/cidade. Atualizado ao salvar.",
		"project_type": "Classificação da obra: Residencial, Comercial, Industrial, Infraestrutura, Reforma ou Outro.",
		"status": "Situação atual: Orçamento, Em andamento, Paralisada, Concluída ou Cancelada.",
		"start_date": "Data de início prevista ou efetiva da obra.",
		"expected_delivery": "Data prevista para conclusão ou entrega da obra.",
		"address_cep": "CEP do local da obra (apenas dígitos).",
		"address_street": "Logradouro do endereço da obra.",
		"address_number": "Número do imóvel ou lote.",
		"address_district": "Bairro onde a obra será executada.",
		"city": "Município da obra. Entra no título automático do registro.",
		"address_uf": "Unidade federativa (UF) do endereço da obra.",
		"construction_area": "Área total construída em metros quadrados (m²).",
		"current_contract_value": "Soma dos valores vigentes dos contratos desta obra. Atualizado automaticamente.",
		"commission_outstanding": "Total de comissões a receber vinculadas a esta obra. Visível apenas para Engenharia Manager.",
		"commission_summary_panel": "Resumo das comissões da obra. Clique para abrir a lista completa. Visível apenas para Engenharia Manager.",
		"physical_progress": "Avanço físico global da obra (%). Calculado a partir das etapas e medições.",
		"responsible_engineer": "Nome do engenheiro responsável técnico pela obra.",
		"crea_number": "Número de registro no CREA do responsável técnico.",
		"art_number": "Número da ART principal vinculada à obra.",
		"property_registration": "Matrícula do imóvel no cartório de registro.",
		"gps_coordinates": "Coordenadas geográficas do terreno (opcional).",
		"budget_revision": "Número da revisão de orçamento vigente. Controla qual versão dos itens está ativa.",
		"default_bdi_percent": "Percentual de BDI padrão aplicado a novos itens do projeto. Visível apenas para Engenharia Manager.",
		"budget_revisions": "Histórico de revisões de orçamento com totais por versão. Visível apenas para Engenharia Manager.",
		"spec_project_total": "Soma dos valores dos itens técnicos na revisão vigente. Atualiza ao salvar itens. Visível apenas para Engenharia Manager.",
		"spec_items_summary_panel": "Tabela resumida dos itens técnicos da obra. Visível apenas para Engenharia Manager.",
		"observations": "Observações gerais sobre a obra.",
	},
	"Customer": {
		"person_type": "Pessoa Física ou Pessoa Jurídica. Define quais documentos são obrigatórios.",
		"customer_name": "Nome completo (PF) ou razão social (PJ).",
		"trade_name": "Nome fantasia da empresa (apenas pessoa jurídica).",
		"cpf": "CPF do cliente. Apenas dígitos, validado automaticamente. Obrigatório para pessoa física.",
		"rg": "Documento de identidade (pessoa física).",
		"cnpj": "CNPJ do cliente (numérico ou alfanumérico). Sem máscara no banco; validado automaticamente. Obrigatório para pessoa jurídica.",
		"nationality": "Nacionalidade do cliente (pessoa física).",
		"marital_status": "Estado civil (pessoa física).",
		"profession": "Profissão declarada (pessoa física).",
		"legal_representative": "Nome do representante legal (pessoa jurídica).",
		"legal_representative_cpf": "CPF do representante legal, com validação automática.",
		"legal_representative_role": "Cargo do representante legal na empresa.",
		"legal_representative_nationality": "Nacionalidade do representante legal.",
		"contacts": "Telefones e e-mails de contato do cliente.",
		"addresses": "Endereços do cliente. O principal é usado em documentos gerados.",
		"observations": "Anotações internas sobre o cliente.",
	},
	"Customer Contact": {
		"contact_name": "Nome da pessoa de contato.",
		"contact_type": "Relação com o cliente: Principal, Cônjuge, Responsável ou Outro.",
		"phone": "Telefone fixo com DDD (10 dígitos).",
		"mobile": "Celular com DDD (11 dígitos).",
		"email": "E-mail de contato. Armazenado em minúsculas.",
		"notes": "Observações sobre este contato.",
	},
	"Customer Address": {
		"address_type": "Finalidade do endereço: Residencial, Comercial, Correspondência ou Outro.",
		"cep": "CEP do endereço (apenas dígitos).",
		"street": "Logradouro (rua, avenida, etc.).",
		"number": "Número do imóvel.",
		"complement": "Complemento (apto, sala, bloco).",
		"district": "Bairro.",
		"city": "Cidade.",
		"state": "UF (sigla de dois caracteres).",
		"is_primary": "Marque o endereço principal usado em documentos e propostas.",
	},
	"Engineering Contract": {
		"project": "Obra vinculada a este contrato. O cliente é preenchido automaticamente.",
		"customer": "Preenchido automaticamente a partir da obra selecionada.",
		"title": "Título automático no formato ID — cliente.",
		"status": "Situação: Vigente, Encerrado, Cancelado ou Quitado.",
		"base_value": "Valor original do contrato antes de aditivos.",
		"current_value": "Valor atual considerando aditivos. Calculado automaticamente.",
		"adjustment_index": "Índice de reajuste contratual: INCC, IPCA, IGP-M ou Nenhum.",
		"technical_retention_pct": "Percentual de retenção técnica sobre parcelas.",
		"late_fee_pct": "Percentual de multa por atraso no pagamento.",
		"daily_interest_pct": "Juros diários aplicados após o vencimento.",
		"installment_count": "Quantidade de parcelas planejadas.",
		"first_installment_date": "Vencimento da primeira parcela.",
		"installment_value": "Valor médio por parcela. Calculado a partir do valor atual.",
		"installments": "Parcelas do contrato. Ao salvar, o sistema gera ou atualiza os pagamentos correspondentes.",
		"amendments": "Aditivos contratuais (acréscimos ou reduções). Use o botão Aplicar Aditivo para recalcular parcelas.",
		"observations": "Observações contratuais e anotações internas.",
	},
	"Engineering Contract Installment": {
		"due_date": "Data de vencimento da parcela.",
		"amount": "Valor previsto da parcela.",
		"received_amount": "Valor efetivamente recebido (quando quitada).",
		"status": "Pendente, Vencido, Recebido ou Cancelado. Sincronizado com o pagamento vinculado.",
		"description": "Descrição exibida na parcela e no pagamento gerado.",
		"receipt_date": "Data em que o pagamento foi recebido.",
		"nf_number": "Número da nota fiscal vinculada ao recebimento.",
		"bank_account": "Conta bancária utilizada no recebimento.",
		"late_fee": "Juros ou multa cobrados por atraso.",
		"installment_origin_id": "Identificador interno para sincronização com pagamentos. Gerado automaticamente.",
		"payment": "Pagamento vinculado a esta parcela. Preenchido pela sincronização automática.",
	},
	"Engineering Contract Amendment": {
		"amendment_date": "Data de assinatura ou registro do aditivo.",
		"amendment_type": "Adição (aumenta o valor) ou Redução (diminui o valor).",
		"amount": "Valor do aditivo em reais.",
		"description": "Descrição do motivo ou escopo do aditivo.",
	},
	"Subcontract": {
		"project": "Obra onde o serviço do prestador será executado.",
		"customer": "Preenchido automaticamente a partir da obra.",
		"supplier": "Fornecedor ou prestador contratado (ex.: pedreiro, eletricista).",
		"funded_by": "Escritório: entra no seu fluxo de caixa. Cliente: só registro — o cliente paga o prestador direto.",
		"cost_category": "Categoria para relatórios: Mão de obra, Materiais, etc.",
		"stage": "Etapa da obra onde o serviço se aplica (opcional).",
		"description": "Detalhe do serviço contratado (ex.: reboco do bloco A).",
		"total_value": "Valor total acordado. Pode ser ajustado — registre o motivo em Observações de aditivo.",
		"total_paid": "Soma dos pagamentos abaixo. Calculado automaticamente.",
		"outstanding": "Saldo a pagar (Valor Total menos Total Pago). Calculado automaticamente.",
		"status": "Atualiza sozinho: Aberta, Parcial, Paga ou Cancelada (manual).",
		"amendment_remarks": "Motivo da alteração quando mudar o Valor Total acordado.",
		"payments": "Registre cada pagamento ao prestador com data, valor e comprovante.",
	},
	"Subcontract Payment": {
		"payment_date": "Data em que o pagamento foi efetuado ao prestador.",
		"amount": "Valor pago nesta parcela.",
		"payment_method": "Forma de pagamento: PIX, TED, Dinheiro, Cartão, Boleto ou Outro.",
		"reference": "Referência do comprovante: PIX, TED, NF ou outro.",
		"receipt": "Anexe o comprovante de pagamento (imagem ou PDF).",
		"remarks": "Observações sobre este pagamento (opcional).",
	},
	"Commission": {
		"construction_project": "Obra que gerou esta comissão.",
		"commission_type": "Tipo: Pré-Moldado ou Outro.",
		"supplier_name": "Nome da empresa que paga a comissão.",
		"supplier_tax_id": "CNPJ da empresa pagadora (opcional). Validado automaticamente.",
		"description": "Detalhes ou condições da comissão.",
		"title": "Título automático com ID e fornecedor.",
		"total_value": "Valor total da comissão acordada.",
		"total_paid": "Soma dos pagamentos registrados abaixo. Calculado automaticamente.",
		"outstanding": "Saldo a receber (Valor Total menos Total Pago). Calculado automaticamente.",
		"status": "Atualiza sozinho: Open, Partially Paid, Paid ou Cancelled.",
		"payments": "Registre cada pagamento recebido com data, valor e comprovante.",
	},
	"Commission Payment": {
		"payment_date": "Data em que o pagamento foi recebido.",
		"amount": "Valor recebido neste pagamento.",
		"reference": "Referência do comprovante: PIX, TED, NF ou outro.",
		"receipt": "Anexe o comprovante de pagamento (imagem ou PDF).",
		"remarks": "Observações sobre este pagamento.",
	},
	"Payment": {
		"title": "Título automático com ID e descritor.",
		"project": "Obra vinculada. Preenchido automaticamente quando gerado a partir de contrato.",
		"customer": "Preenchido automaticamente a partir da obra.",
		"origin_type": "Origem do recebível: Parcela do Contrato ou Despesa Reembolsável.",
		"contract": "Contrato que originou este pagamento (quando aplicável).",
		"installment_number": "Número sequencial da parcela no contrato.",
		"description": "Descrição da parcela ou recebível.",
		"installment_origin_id": "Identificador de sincronização com a parcela do contrato.",
		"synced_at": "Data e hora da última sincronização automática com o contrato.",
		"manual_override": "Quando marcado, o sistema não sobrescreve este pagamento na sincronização.",
		"amount": "Valor da parcela ou recebível.",
		"received_amount": "Valor efetivamente recebido.",
		"due_date": "Data de vencimento.",
		"received_date": "Data em que o pagamento foi efetivamente recebido.",
		"status": "Pendente, Vencido (atualizado automaticamente), Recebido, Cancelado ou Renegociado.",
		"nf_number": "Número da nota fiscal do recebimento.",
		"bank_account": "Conta bancária de destino.",
		"late_fee": "Juros ou multa por atraso.",
		"notes": "Observações internas sobre o pagamento.",
		"receipt": "Comprovante de recebimento anexado.",
	},
	"Work Cost": {
		"project": "Obra onde este custo foi incorrido.",
		"customer": "Preenchido automaticamente a partir da obra.",
		"title": "Título automático do lançamento.",
		"cost_category": "Categoria: Materiais, Mão de obra, Equipamentos, etc.",
		"supplier": "Fornecedor ou prestador de serviço (opcional).",
		"stage": "Etapa da obra onde o custo se aplica (opcional).",
		"description": "Detalhe do que foi comprado ou contratado.",
		"nf_number": "Número da nota fiscal do custo.",
		"cost_center": "Centro de custo contábil (opcional).",
		"amount": "Valor do custo em reais.",
		"date": "Data do pagamento ou da nota fiscal.",
		"funded_by": "Escritório: entra no seu fluxo de caixa. Cliente: só registro — quem paga é o cliente.",
		"payment_method": "Forma de pagamento: PIX, TED, Dinheiro, Cartão, Boleto ou Outro.",
		"status": "Pago, Pendente ou Cancelado.",
		"receipt": "Comprovante ou nota fiscal anexada.",
	},
	"Reimbursable Expense": {
		"project": "Obra relacionada à despesa.",
		"customer": "Preenchido automaticamente a partir da obra.",
		"title": "Título automático com ID e descrição.",
		"expense_category": "Categoria da despesa (mesmo cadastro de Categorias de Custo).",
		"supplier": "Fornecedor ou órgão que recebeu o pagamento (opcional).",
		"description": "Descrição do que foi pago pelo escritório.",
		"status": "A reembolsar, Reembolsado ou Cancelado.",
		"payment": "Pagamento gerado para cobrança do cliente (quando aplicável).",
		"amount": "Valor pago pelo escritório a ser reembolsado.",
		"payment_date": "Data em que o escritório realizou o pagamento.",
		"await_client_reimbursement": "Marque quando o cliente ainda deve devolver o valor.",
		"client_reimbursed_date": "Data em que o cliente efetuou o reembolso.",
		"receipt": "Comprovante da despesa paga pelo escritório.",
	},
	"Project Item": {
		"project": "Obra onde este item será utilizado.",
		"technical_item": "Modelo do catálogo técnico. Parâmetros e fórmulas são carregados automaticamente.",
		"instance_label": "Rótulo para diferenciar instâncias (ex.: Pilar P1, Laje térreo).",
		"stage": "Etapa ou pavimento da obra (opcional).",
		"quantity": "Quantidade de unidades deste item na obra.",
		"unit": "Unidade de medida herdada do item técnico.",
		"pricing_mode": "Fórmula (cálculo automático) ou Composição de custos (insumos detalhados).",
		"budget_revision": "Revisão de orçamento à qual este item pertence.",
		"bdi_percent": "Percentual de BDI aplicado neste item.",
		"direct_cost": "Custo direto antes do BDI (modo composição).",
		"total_value": "Valor total calculado pelas fórmulas ou composição. Atualiza ao salvar.",
		"title": "Título automático com item, quantidade e resultado principal.",
		"parameter_values": "Parâmetros de entrada do item técnico. Preencha os valores para esta obra.",
		"unit_price": "Preço unitário calculado ou informado conforme o modo de precificação.",
		"cost_components": "Insumos detalhados quando o modo é Composição de custos.",
		"computed_outputs": "Resultados calculados automaticamente pelas fórmulas do item técnico.",
	},
	"Project Item Parameter": {
		"field_key": "Chave usada nas fórmulas (definida no item técnico).",
		"label": "Nome exibido do parâmetro.",
		"value": "Valor informado para esta obra.",
		"unit": "Unidade de medida do parâmetro.",
		"data_type": "Tipo do valor: Número, Texto ou Sim-Não.",
		"required": "Indica se o parâmetro é obrigatório para calcular os resultados.",
	},
	"Project Item Output": {
		"output_key": "Chave interna do resultado calculado.",
		"label": "Nome exibido do resultado (ex.: Volume, Total).",
		"role": "Papel do resultado no sistema (valor, volume, área, prévia).",
		"value": "Valor calculado. Atualizado automaticamente ao salvar.",
		"unit": "Unidade do resultado calculado.",
	},
	"Project Item Cost Component": {
		"description": "Descrição do insumo ou serviço na composição.",
		"supplier": "Fornecedor do insumo (opcional).",
		"quantity": "Quantidade do insumo.",
		"unit": "Unidade de medida do insumo.",
		"unit_cost": "Custo unitário do insumo.",
		"amount": "Valor total da linha (quantidade × custo unitário).",
	},
	"Technical Item": {
		"item_name": "Nome do item no catálogo. Será o identificador único.",
		"item_key": "Chave interna para fórmulas (sem espaços ou acentos).",
		"category": "Categoria para organização: Estrutural, Elétrica, Hidráulica, etc.",
		"data_type": "Tipo de dado legado do cadastro. Prefira definir tipos nos campos abaixo.",
		"default_unit": "Unidade padrão herdada pelos itens do projeto (m³, m², kg, etc.).",
		"fields": "Parâmetros de entrada preenchidos ao usar este item em uma obra.",
		"outputs": "Resultados calculados por fórmulas. Defina o Papel de cada saída.",
	},
	"Technical Item Field": {
		"field_key": "Chave usada nas fórmulas (ex.: comprimento). Sem espaços ou acentos.",
		"label": "Nome exibido ao usuário (ex.: Comprimento).",
		"unit": "Unidade de medida do parâmetro (opcional).",
		"data_type": "Tipo do valor: Número, Texto ou Sim-Não.",
		"default_value": "Valor sugerido ao adicionar o item em uma obra (opcional).",
		"required": "Marque se o parâmetro deve ser obrigatório na obra.",
		"sort_order": "Ordem de exibição do parâmetro no formulário.",
	},
	"Technical Item Output": {
		"output_key": "Chave usada nas fórmulas e referências. Sem espaços ou acentos.",
		"label": "Nome exibido do resultado (ex.: Volume, Custo Total).",
		"unit": "Unidade do resultado (m³, R$, etc.).",
		"formula": "Expressão matemática usando as chaves dos parâmetros. Ex.: comprimento * largura * altura",
		"sort_order": "Ordem de cálculo. Resultados anteriores podem ser usados nos seguintes.",
	},
	"Project Stage": {
		"project": "Obra à qual esta etapa pertence.",
		"stage_type": "Tipo de etapa do catálogo (Fundação, Estrutura, Alvenaria, etc.).",
		"status": "Não iniciada, Em andamento ou Concluída.",
		"progress": "Percentual de conclusão desta etapa (0 a 100).",
		"weight": "Peso relativo da etapa no avanço físico global da obra.",
		"stage_value": "Valor orçado ou medido para esta etapa.",
		"order": "Ordem de exibição e sequenciamento da etapa.",
		"title": "Título automático da etapa.",
		"start_date": "Data de início prevista ou real.",
		"expected_end": "Data prevista de conclusão.",
		"actual_end": "Data real de conclusão da etapa.",
	},
	"Deadline": {
		"title": "Título automático do prazo.",
		"project": "Obra vinculada ao prazo.",
		"customer": "Preenchido automaticamente a partir da obra.",
		"due_date": "Data limite. O sistema alerta quando o prazo se aproxima ou vence.",
		"status": "Pendente, Concluído ou Vencido. Vencido é atualizado automaticamente.",
		"deadline_type": "Classificação: Projeto, Cliente, Órgão ou Outro.",
		"public_agency": "Órgão público relacionado (prefeitura, CREA, etc.), quando aplicável.",
		"description": "Descrição do compromisso ou entrega esperada.",
		"priority": "Alta, Média ou Baixa — usada em alertas e no painel.",
		"assigned_to": "Usuário responsável pelo cumprimento do prazo.",
		"notify_days_before": "Quantos dias antes do vencimento enviar notificação.",
		"notes": "Observações adicionais sobre o prazo.",
	},
	"Task": {
		"project": "Obra relacionada (opcional).",
		"customer": "Preenchido automaticamente a partir da obra.",
		"stage": "Etapa da obra vinculada (opcional).",
		"subject": "Descrição curta da tarefa. Aparece como título na lista e no Kanban.",
		"status": "A fazer, Fazendo, Feito ou Cancelada.",
		"priority": "Baixa, Média ou Alta.",
		"due_date": "Prazo para conclusão da tarefa (opcional).",
		"description": "Detalhamento da tarefa e instruções.",
		"assigned_to": "Usuário responsável pela execução.",
		"completed_on": "Data de conclusão. Preenchida automaticamente ao marcar como Feito.",
	},
	"Permit": {
		"project": "Obra vinculada a este protocolo.",
		"customer": "Preenchido automaticamente a partir da obra.",
		"title": "Título automático do protocolo.",
		"permit_type": "Tipo de alvará ou protocolo (cadastro de Tipos de Alvará).",
		"permit_number": "Número do protocolo ou alvará emitido pelo órgão.",
		"public_agency": "Órgão onde o protocolo foi registrado.",
		"status": "Situação junto ao órgão: Pendente, Em análise, Aprovado, etc.",
		"protocol_date": "Data de protocolo ou emissão.",
		"expiry_date": "Data de validade. Gera evento no calendário para controle.",
		"document": "Documento digital do alvará ou protocolo.",
		"art_rrt_number": "Número da ART ou RRT (obrigatório para tipos ART/RRT).",
		"crea_cau_number": "Registro CREA/CAU do profissional responsável.",
		"responsible_professional": "Nome do profissional responsável técnico.",
		"art_validity_date": "Data de validade da ART/RRT.",
		"art_fee": "Valor da taxa paga pela ART/RRT.",
		"art_fee_receipt": "Comprovante do pagamento da taxa.",
	},
	"Construction Measurement": {
		"project": "Obra medida.",
		"customer": "Preenchido automaticamente a partir da obra.",
		"title": "Título automático da medição.",
		"measurement_date": "Data em que a medição foi realizada em campo.",
		"measurement_number": "Número sequencial da medição na obra.",
		"reference_period": "Período de referência (ex.: Março/2026).",
		"status": "Rascunho, Aprovada ou Contestada.",
		"measurement_items": "Etapas medidas com percentual de avanço no período.",
		"total_measured_value": "Valor total medido. Calculado a partir dos itens.",
		"observations": "Observações sobre a medição.",
		"attachment": "Planilha ou relatório de medição anexado.",
	},
	"Construction Measurement Item": {
		"project_stage": "Etapa da obra sendo medida.",
		"stage_description": "Descrição da etapa (preenchida automaticamente).",
		"previous_pct": "Percentual acumulado na medição anterior.",
		"current_pct": "Percentual acumulado atual desta etapa.",
		"increment_pct": "Incremento percentual desta medição. Calculado automaticamente.",
		"stage_value": "Valor orçado da etapa. Herdado da etapa vinculada.",
		"measured_value": "Valor medido no período (incremento × valor da etapa).",
	},
	"Time Log": {
		"title": "Título automático do registro de horas.",
		"project": "Obra onde a atividade foi realizada.",
		"customer": "Preenchido automaticamente a partir da obra.",
		"log_date": "Data da atividade.",
		"assigned_to": "Profissional que registrou ou executou a atividade.",
		"start_time": "Hora de início (usado pelo timer).",
		"end_time": "Hora de término (usado pelo timer).",
		"duration_minutes": "Duração em minutos. Preencha manualmente ou use o timer.",
		"duration_hours": "Duração convertida em horas. Calculada automaticamente.",
		"activity": "Descrição da atividade realizada.",
		"category": "Classificação: Visita de Obra, Reunião, Projeto Técnico, etc.",
		"details": "Detalhes adicionais sobre a atividade.",
		"billable": "Marque se o tempo é cobrável do cliente.",
	},
	"Communication Log": {
		"title": "Título automático do registro.",
		"project": "Obra relacionada à comunicação (opcional).",
		"customer": "Cliente envolvido na comunicação.",
		"communication_date": "Data e hora da comunicação.",
		"communication_type": "Canal: Telefone, WhatsApp, E-mail, Reunião Presencial, etc.",
		"subject": "Assunto principal da comunicação.",
		"summary": "Resumo do que foi tratado.",
		"next_steps": "Próximos passos combinados (opcional).",
		"create_task": "Marque para criar uma tarefa automaticamente a partir deste registro.",
		"task": "Tarefa gerada a partir desta comunicação (quando aplicável).",
	},
	"Supplier": {
		"supplier_name": "Nome ou razão social do fornecedor. Identificador único.",
		"cnpj": "CNPJ do fornecedor (opcional). Validado automaticamente.",
		"category": "Ramo de atuação: Material, Serviço, Mão de obra ou Outro.",
		"phone": "Telefone de contato.",
		"email": "E-mail de contato.",
	},
	"Document Template": {
		"template_name": "Nome do modelo. Identificador único no catálogo.",
		"document_type": "Tipo do documento: Contrato, Proposta, Relatório ou Outro.",
		"description": "Descrição do uso deste modelo.",
		"enabled": "Desmarque para ocultar o modelo na geração de documentos.",
	},
	"Document Kit": {
		"kit_name": "Nome do kit de documentos. Identificador único.",
		"description": "Descrição do conjunto de modelos incluídos.",
		"enabled": "Desmarque para desabilitar o kit na geração em lote.",
		"templates": "Modelos de documento incluídos neste kit.",
	},
	"Document Kit Item": {
		"document_template": "Modelo de documento incluído no kit.",
		"sort_order": "Ordem de exibição e geração no kit.",
	},
	"Engineering Settings": {
		"company_name": "Razão social do escritório. Usada em documentos gerados.",
		"company_cnpj": "CNPJ do escritório. Usado em contratos e documentos oficiais.",
		"company_crea": "Número de registro no CREA do escritório.",
		"company_logo": "Logotipo exibido em documentos gerados (opcional).",
		"default_notify_days": "Dias padrão de antecedência para alertas de prazos.",
		"bank_name": "Nome do banco para dados em propostas e recibos.",
		"bank_agency": "Agência bancária.",
		"bank_account": "Número da conta corrente.",
		"bank_pix": "Chave PIX para recebimentos.",
	},
	"Cost Category": {
		"category_name": "Nome único que identifica esta categoria no sistema.",
	},
	"Stage Type": {
		"stage_name": "Nome único da etapa no catálogo (ex.: Fundação, Estrutura).",
		"default_order": "Ordem padrão de exibição ao criar etapas na obra.",
	},
	"Permit Type": {
		"type_name": "Nome único do tipo de protocolo ou alvará.",
		"is_art_rrt": "Marque se este tipo exige número de ART/RRT no protocolo.",
	},
	"Public Agency": {
		"agency_name": "Nome único do órgão público.",
		"sphere": "Esfera governamental: Municipal, Estadual ou Federal.",
		"city": "Cidade sede do órgão.",
	},
	"Project Budget Revision": {
		"revision_number": "Número sequencial da revisão de orçamento.",
		"revision_date": "Data em que a revisão foi criada.",
		"total_amount": "Valor total do orçamento nesta revisão.",
		"status": "Vigente (ativa) ou Supersedida (histórico).",
		"notes": "Observações sobre o motivo da revisão.",
	},
	"Project Specification": {
		"technical_item": "Modelo técnico de referência (legado).",
		"instance_label": "Identificação da instância na obra.",
		"stage": "Etapa vinculada (opcional).",
		"field_key": "Chave do parâmetro.",
		"label": "Nome do campo.",
		"value": "Valor informado.",
		"unit": "Unidade de medida.",
		"data_type": "Tipo do dado.",
		"required": "Indica se o campo é obrigatório.",
		"remarks": "Observações sobre o parâmetro.",
	},
}

FALLBACK_BY_FIELDTYPE: dict[str, str] = {
	"Link": "Selecione o registro vinculado.",
	"Select": "Escolha a opção adequada ao registro.",
	"Check": "Marque quando a condição se aplicar.",
	"Attach": "Anexe o arquivo correspondente.",
	"Attach Image": "Anexe a imagem correspondente.",
	"Table": "Preencha as linhas da tabela abaixo.",
	"Currency": "Valor em reais (R$).",
	"Percent": "Percentual de 0 a 100.",
	"Date": "Informe a data no formato DD/MM/AAAA.",
	"Datetime": "Informe data e hora.",
	"Int": "Número inteiro.",
	"Float": "Número decimal.",
	"Data": "Texto curto de identificação.",
	"Small Text": "Texto complementar.",
	"Text Editor": "Texto longo com formatação.",
}


def _permlevel_hint(permlevel: int) -> str:
	if permlevel and permlevel > 0:
		return " Visível apenas para Engenharia Manager."
	return ""


def _read_only_hint(read_only: int) -> str:
	if read_only:
		return " Preenchido ou calculado automaticamente pelo sistema."
	return ""


def apply_descriptions(doctype_json_path: Path) -> int:
	with open(doctype_json_path, encoding="utf-8") as f:
		data = json.load(f)

	if data.get("doctype") != "DocType":
		return 0

	doctype_name = data.get("name", "")
	field_map = DESCRIPTIONS.get(doctype_name, {})
	updated = 0

	for field in data.get("fields", []):
		ft = field.get("fieldtype")
		if ft in SKIP_FIELDTYPES:
			continue
		if field.get("description"):
			continue

		fn = field.get("fieldname", "")
		desc = field_map.get(fn)
		if not desc:
			base = FALLBACK_BY_FIELDTYPE.get(ft, "")
			if not base:
				continue
			desc = base
			desc += _read_only_hint(field.get("read_only", 0))
			desc += _permlevel_hint(field.get("permlevel", 0))
		else:
			pl = field.get("permlevel", 0)
			if pl and pl > 0 and "Engenharia Manager" not in desc:
				desc = desc.rstrip(".") + ". Visível apenas para Engenharia Manager."

		field["description"] = desc
		updated += 1

	if updated:
		with open(doctype_json_path, "w", encoding="utf-8") as f:
			json.dump(data, f, indent=1, ensure_ascii=False)
			f.write("\n")

	return updated


def main() -> None:
	root = Path(__file__).resolve().parents[1] / "engenharia" / "doctype"
	total = 0
	for path in sorted(root.glob("*/*.json")):
		count = apply_descriptions(path)
		if count:
			print(f"{path.parent.name}: {count} fields")
			total += count
	print(f"Total: {total} descriptions added")


if __name__ == "__main__":
	main()
