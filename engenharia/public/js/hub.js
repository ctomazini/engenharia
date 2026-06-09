/* ═══════════════════════════════════════════════════════════
   eng_hub — Render functions for Construction Project hub tabs
   ═══════════════════════════════════════════════════════════ */

function eng_hub_load(frm) {
	frappe.call({
		method: "engenharia.project_hub.get_project_hub_data",
		args: { project: frm.doc.name },
		callback(r) {
			const data = r.message || {};
			eng_hub_render_stages(frm, data.stages || []);
			eng_hub_render_financial(frm, data.financial);
			eng_hub_render_deadlines(frm, data.deadlines || []);
			eng_hub_render_permits(frm, data.permits || []);
			eng_hub_render_tasks(frm, data.tasks || []);
			eng_hub_render_communications(frm, data.communications || []);
			eng_hub_render_measurements(frm, data.measurements || []);
			eng_hub_render_timelogs(frm, data.timelogs || []);
		},
	});
}

function eng_hub_render_stages(frm, stages) {
	const $w = frm.fields_dict.stages_panel?.$wrapper;
	if (!$w) return;

	if (!stages.length) {
		$w.html(
			_eng_hub_empty("📐", __("Nenhuma etapa cadastrada"), __("+ Nova Etapa"), "new-stage")
		);
		$w.find('[data-hub-action="new-stage"]').on("click", () => {
			frappe.new_doc("Project Stage", { project: frm.doc.name });
		});
		return;
	}

	const totalWeight = stages.reduce((sum, row) => sum + (row.weight || 0), 0);
	const weightOk = Math.abs(totalWeight - 100) < 0.01;
	const weightHtml = `<div class="eng-hub-weight-alert eng-hub-weight-alert--${
		weightOk ? "ok" : "warn"
	}">
		⚖️ ${__("Soma dos pesos")}: <strong>${totalWeight.toFixed(1)}%</strong>
		${weightOk ? "" : " — " + __("ideal: 100%")}
	</div>`;

	const statusMap = { Concluída: "green", "Em andamento": "blue", "Não iniciada": "gray" };
	const bars = stages
		.map((stage) => {
			const pct = Math.min(100, Math.max(0, stage.progress || 0));
			const fillClass =
				pct >= 100 ? "--completed" : pct > 0 ? "--active" : "--not-started";
			const badgeColor = statusMap[stage.status] || "gray";
			return `<div class="eng-hub-progress" data-stage="${frappe.utils.escape_html(
				stage.name
			)}" title="${__("Clique para editar")}">
			<span class="eng-hub-progress__label">${frappe.utils.escape_html(stage.stage_type)}</span>
			<div class="eng-hub-progress__track">
				<div class="eng-hub-progress__fill eng-hub-progress__fill${fillClass}" style="width:${pct}%"></div>
			</div>
			<span class="eng-hub-progress__value">${pct.toFixed(0)}%</span>
			<span class="eng-hub-badge eng-hub-badge--${badgeColor}">${stage.status || ""}</span>
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">🏗️</span>
				${__("Etapas da Obra")}
				<span class="eng-hub-panel__count">${stages.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-stage">
				${__("+ Etapa")}
			</button>
		</div>
		${weightHtml}
		${bars}
	</div>`);

	$w.find('[data-hub-action="new-stage"]').on("click", () => {
		frappe.new_doc("Project Stage", { project: frm.doc.name });
	});
	$w.find(".eng-hub-progress").on("click", function () {
		eng_hub_edit_stage(frm, $(this).attr("data-stage"));
	});
}

function eng_hub_edit_stage(frm, stage_name) {
	frappe.call({
		method: "frappe.client.get",
		args: { doctype: "Project Stage", name: stage_name },
		callback(r) {
			const stage = r.message;
			const dialog = new frappe.ui.Dialog({
				title: __("Atualizar: {0}", [stage.stage_type]),
				fields: [
					{
						fieldname: "progress",
						fieldtype: "Percent",
						label: __("Avanço (%)"),
						default: stage.progress,
					},
					{
						fieldname: "status",
						fieldtype: "Select",
						label: __("Status"),
						options: "Não iniciada\nEm andamento\nConcluída",
						default: stage.status,
					},
				],
				primary_action_label: __("Salvar"),
				primary_action(values) {
					frappe.call({
						method: "frappe.client.set_value",
						args: {
							doctype: "Project Stage",
							name: stage_name,
							fieldname: {
								progress: values.progress,
								status: values.status,
							},
						},
						callback() {
							dialog.hide();
							frm.reload_doc();
						},
					});
				},
			});
			dialog.show();
		},
	});
}

function eng_hub_render_financial(frm, financial) {
	const panels = ["financial_summary_panel", "installments_panel", "costs_panel"];
	if (!financial) {
		panels.forEach((panel) => {
			if (frm.fields_dict[panel]) {
				frm.fields_dict[panel].$wrapper.html("");
			}
		});
		return;
	}

	_eng_hub_render_financial_summary(frm, financial.summary);
	_eng_hub_render_installments(frm, financial.installments);
	_eng_hub_render_costs(frm, financial);
}

function _eng_hub_render_financial_summary(frm, summary) {
	const $w = frm.fields_dict.financial_summary_panel?.$wrapper;
	if (!$w || !summary) return;

	const total = summary.total_contracted || 1;
	const pctReceived = Math.round((summary.total_received / total) * 100);
	const pctCosts = Math.round((summary.total_costs / total) * 100);
	const pctPending = Math.max(0, 100 - pctReceived - pctCosts);

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">💰</span>
				${__("Resumo Financeiro")}
			</h3>
		</div>
		<div class="eng-hub-kpi-row">
			<div class="eng-hub-kpi">
				<div class="eng-hub-kpi__value" style="color:var(--blue-500)">${format_currency(
					summary.total_contracted
				)}</div>
				<div class="eng-hub-kpi__label">${__("Contratado")}</div>
			</div>
			<div class="eng-hub-kpi">
				<div class="eng-hub-kpi__value" style="color:var(--green-600)">${format_currency(
					summary.total_received
				)}</div>
				<div class="eng-hub-kpi__label">${__("Recebido")}</div>
			</div>
			<div class="eng-hub-kpi">
				<div class="eng-hub-kpi__value" style="color:var(--orange-500)">${format_currency(
					summary.total_pending
				)}</div>
				<div class="eng-hub-kpi__label">${__("A Receber")}</div>
			</div>
			<div class="eng-hub-kpi">
				<div class="eng-hub-kpi__value" style="color:var(--red-500)">${format_currency(
					summary.total_costs + summary.total_subcontracts
				)}</div>
				<div class="eng-hub-kpi__label">${__("Custos + Sub")}</div>
			</div>
			<div class="eng-hub-kpi">
				<div class="eng-hub-kpi__value" style="color:${
					summary.margin >= 0 ? "var(--green-600)" : "var(--red-600)"
				}">${format_currency(summary.margin)}</div>
				<div class="eng-hub-kpi__label">${__("Margem")}</div>
			</div>
		</div>
		<div class="eng-hub-stacked-bar">
			<div class="eng-hub-stacked-bar__segment" style="width:${pctReceived}%;background:var(--green-500)" title="${__(
				"Recebido"
			)}"></div>
			<div class="eng-hub-stacked-bar__segment" style="width:${pctCosts}%;background:var(--red-500)" title="${__(
				"Custos"
			)}"></div>
			<div class="eng-hub-stacked-bar__segment" style="width:${pctPending}%;background:var(--orange-500);opacity:.4" title="${__(
				"Pendente"
			)}"></div>
		</div>
	</div>`);
}

function _eng_hub_render_installments(frm, installments) {
	const $w = frm.fields_dict.installments_panel?.$wrapper;
	if (!$w) return;

	if (!installments || !installments.length) {
		$w.html(`<div class="eng-hub-empty">${__("Nenhuma parcela registrada.")}</div>`);
		return;
	}

	const rows = installments
		.map((row) => {
			const badge = _eng_hub_status_badge(row.status);
			const dt = row.due_date ? frappe.datetime.str_to_user(row.due_date) : "—";
			return `<div class="eng-hub-list-row" data-route="Form/Engineering Contract/${frappe.utils.escape_html(
				row.contract
			)}">
			<div class="eng-hub-list-row__main">
				<span style="color:var(--text-muted);margin-right:4px">#${row.idx}</span>
				${dt}
				<span class="eng-hub-list-row__secondary">${frappe.utils.escape_html(
					row.contract_title || ""
				)}</span>
			</div>
			<div class="eng-hub-list-row__value">${format_currency(row.amount)}</div>
			${badge}
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">📋</span>
				${__("Parcelas")}
				<span class="eng-hub-panel__count">${installments.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="list-contracts">
				${__("Ver Contratos")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="list-contracts"]').on("click", () => {
		frappe.set_route("List", "Engineering Contract", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function _eng_hub_render_costs(frm, financial) {
	const $w = frm.fields_dict.costs_panel?.$wrapper;
	if (!$w) return;

	const costs = financial.costs || [];
	const subs = financial.subcontracts || [];

	if (!costs.length && !subs.length) {
		$w.html(_eng_hub_empty("📊", __("Nenhum custo registrado"), __("+ Custo"), "new-cost"));
		$w.find('[data-hub-action="new-cost"]').on("click", () => {
			frappe.new_doc("Work Cost", { project: frm.doc.name });
		});
		return;
	}

	const byCategory = {};
	costs.forEach((cost) => {
		const cat = cost.cost_category || __("Sem categoria");
		byCategory[cat] = (byCategory[cat] || 0) + (cost.amount || 0);
	});

	const catRows = Object.entries(byCategory)
		.sort(([, a], [, b]) => b - a)
		.map(
			([cat, val]) => `<div class="eng-hub-list-row">
			<div class="eng-hub-list-row__main">${frappe.utils.escape_html(cat)}</div>
			<div class="eng-hub-list-row__value">${format_currency(val)}</div>
		</div>`
		)
		.join("");

	const subRows = subs.length
		? `<div class="eng-hub-subgroup">
			<div class="eng-hub-subgroup__title">${__("Subcontratos")}</div>
			${subs
				.map(
					(sub) => `<div class="eng-hub-list-row" data-route="Form/Subcontract/${frappe.utils.escape_html(
						sub.name
					)}">
				<div class="eng-hub-list-row__main">${frappe.utils.escape_html(sub.title || sub.name)}</div>
				<div class="eng-hub-list-row__value">${format_currency(sub.total_value)}</div>
				<span class="eng-hub-badge eng-hub-badge--${
					flt(sub.total_paid) >= flt(sub.total_value) ? "green" : "orange"
				}">
					${format_currency(sub.total_paid || 0)} ${__("pago")}
				</span>
			</div>`
				)
				.join("")}
		</div>`
		: "";

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">📊</span>
				${__("Custos")}
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-cost">
				${__("+ Custo")}
			</button>
		</div>
		${catRows}
		${subRows}
	</div>`);

	$w.find('[data-hub-action="new-cost"]').on("click", () => {
		frappe.new_doc("Work Cost", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_deadlines(frm, deadlines) {
	const $w = frm.fields_dict.deadlines_panel?.$wrapper;
	if (!$w) return;

	if (!deadlines.length) {
		$w.html(_eng_hub_empty("📅", __("Nenhum prazo cadastrado"), __("+ Prazo"), "new-deadline"));
		$w.find('[data-hub-action="new-deadline"]').on("click", () => {
			frappe.new_doc("Deadline", { project: frm.doc.name });
		});
		return;
	}

	const items = deadlines
		.map((deadline) => {
			const dt = deadline.due_date ? frappe.datetime.str_to_user(deadline.due_date) : "—";
			let daysHtml = "";
			if (deadline.days_remaining !== null && deadline.urgency !== "done") {
				if (deadline.days_remaining < 0) {
					daysHtml = `<span style="color:var(--red-500);font-weight:600">${Math.abs(
						deadline.days_remaining
					)}d ${__("atrasado")}</span>`;
				} else if (deadline.days_remaining === 0) {
					daysHtml = `<span style="color:var(--orange-500);font-weight:600">${__(
						"Vence hoje!"
					)}</span>`;
				} else {
					daysHtml = `<span>${deadline.days_remaining}d</span>`;
				}
			}
			return `<div class="eng-hub-timeline-item" data-route="Form/Deadline/${frappe.utils.escape_html(
				deadline.name
			)}">
			<div class="eng-hub-timeline-dot eng-hub-timeline-dot--${deadline.urgency}"></div>
			<div style="flex:1">
				<div class="eng-hub-timeline-title">${frappe.utils.escape_html(
					deadline.title || deadline.name
				)}</div>
				<div class="eng-hub-timeline-meta">
					<span>${dt}</span>
					${daysHtml ? "<span>·</span>" + daysHtml : ""}
					${
						deadline.public_agency
							? "<span>·</span><span>" +
							  frappe.utils.escape_html(deadline.public_agency) +
							  "</span>"
							: ""
					}
				</div>
			</div>
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">📅</span>
				${__("Prazos")}
				<span class="eng-hub-panel__count">${deadlines.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-deadline">
				${__("+ Prazo")}
			</button>
		</div>
		${items}
	</div>`);

	$w.find('[data-hub-action="new-deadline"]').on("click", () => {
		frappe.new_doc("Deadline", { project: frm.doc.name });
	});
	$w.find(".eng-hub-timeline-item[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_permits(frm, permits) {
	const $w = frm.fields_dict.permits_panel?.$wrapper;
	if (!$w) return;

	if (!permits.length) {
		$w.html(_eng_hub_empty("🏛️", __("Nenhum alvará registrado"), __("+ Protocolo"), "new-permit"));
		$w.find('[data-hub-action="new-permit"]').on("click", () => {
			frappe.new_doc("Permit", { project: frm.doc.name });
		});
		return;
	}

	const statusMap = {
		Deferido: "green",
		Vigente: "green",
		"Em análise": "orange",
		Protocolado: "blue",
		Indeferido: "red",
		Vencido: "red",
	};

	const rows = permits
		.map((permit) => {
			const badge = `<span class="eng-hub-badge eng-hub-badge--${
				statusMap[permit.status] || "gray"
			}">${permit.status || ""}</span>`;
			return `<div class="eng-hub-list-row" data-route="Form/Permit/${frappe.utils.escape_html(
				permit.name
			)}">
			<div class="eng-hub-list-row__icon">🏛️</div>
			<div class="eng-hub-list-row__main">
				${frappe.utils.escape_html(permit.permit_type || "")}
				${
					permit.permit_number
						? " — " + frappe.utils.escape_html(permit.permit_number)
						: ""
				}
			</div>
			${badge}
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">🏛️</span>
				${__("Alvarás e Protocolos")}
				<span class="eng-hub-panel__count">${permits.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-permit">
				${__("+ Protocolo")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-permit"]').on("click", () => {
		frappe.new_doc("Permit", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_tasks(frm, tasks) {
	const $w = frm.fields_dict.tasks_panel?.$wrapper;
	if (!$w) return;

	if (!tasks.length) {
		$w.html(_eng_hub_empty("✅", __("Nenhuma tarefa pendente"), __("+ Tarefa"), "new-task"));
		$w.find('[data-hub-action="new-task"]').on("click", () => {
			frappe.new_doc("Task", { project: frm.doc.name });
		});
		return;
	}

	const prioColor = { Urgente: "red", Alta: "orange", Média: "blue", Baixa: "gray" };
	const rows = tasks
		.map((task) => {
			const pc = prioColor[task.priority] || "gray";
			const dt = task.due_date ? frappe.datetime.str_to_user(task.due_date) : "";
			const dotClass =
				task.priority === "Urgente"
					? "overdue"
					: task.priority === "Alta"
					? "urgent"
					: "normal";
			return `<div class="eng-hub-list-row" data-route="Form/Task/${frappe.utils.escape_html(
				task.name
			)}">
			<div class="eng-hub-timeline-dot eng-hub-timeline-dot--${dotClass}" style="margin:0 8px 0 4px"></div>
			<div class="eng-hub-list-row__main">
				${frappe.utils.escape_html(task.subject)}
				${dt ? '<span class="eng-hub-list-row__secondary">' + dt + "</span>" : ""}
			</div>
			<span class="eng-hub-badge eng-hub-badge--${pc}">${task.priority || ""}</span>
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">✅</span>
				${__("Tarefas Pendentes")}
				<span class="eng-hub-panel__count">${tasks.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-task">
				${__("+ Tarefa")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-task"]').on("click", () => {
		frappe.new_doc("Task", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_communications(frm, communications) {
	const $w = frm.fields_dict.communications_panel?.$wrapper;
	if (!$w) return;

	if (!communications.length) {
		$w.html(
			_eng_hub_empty("💬", __("Nenhuma comunicação registrada"), __("+ Comunicação"), "new-comm")
		);
		$w.find('[data-hub-action="new-comm"]').on("click", () => {
			frappe.new_doc("Communication Log", { project: frm.doc.name });
		});
		return;
	}

	const icons = {
		Telefone: "📞",
		WhatsApp: "💬",
		Email: "📧",
		"Reunião Presencial": "🤝",
		"Reunião Virtual": "💻",
		Outro: "📝",
	};

	const rows = communications
		.map((comm) => {
			const icon = icons[comm.communication_type] || "📝";
			const dt = comm.communication_date
				? frappe.datetime.str_to_user(comm.communication_date)
				: "";
			return `<div class="eng-hub-list-row" data-route="Form/Communication Log/${frappe.utils.escape_html(
				comm.name
			)}">
			<div class="eng-hub-list-row__icon">${icon}</div>
			<div class="eng-hub-list-row__main">
				${frappe.utils.escape_html(comm.subject || comm.title || comm.name)}
				<span class="eng-hub-list-row__secondary">${dt}</span>
			</div>
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">💬</span>
				${__("Comunicações")}
				<span class="eng-hub-panel__count">${communications.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-comm">
				${__("+ Comunicação")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-comm"]').on("click", () => {
		frappe.new_doc("Communication Log", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_measurements(frm, measurements) {
	const $w = frm.fields_dict.measurements_panel?.$wrapper;
	if (!$w) return;

	if (!measurements.length) {
		$w.html(
			_eng_hub_empty("📏", __("Nenhuma medição registrada"), __("+ Medição"), "new-measurement")
		);
		$w.find('[data-hub-action="new-measurement"]').on("click", () => {
			frappe.new_doc("Construction Measurement", { project: frm.doc.name });
		});
		return;
	}

	const rows = measurements
		.map((measurement) => {
			const dt = measurement.measurement_date
				? frappe.datetime.str_to_user(measurement.measurement_date)
				: "";
			return `<div class="eng-hub-list-row" data-route="Form/Construction Measurement/${frappe.utils.escape_html(
				measurement.name
			)}">
			<div class="eng-hub-list-row__icon">📏</div>
			<div class="eng-hub-list-row__main">
				${frappe.utils.escape_html(
					measurement.reference_period || measurement.title || measurement.name
				)}
				<span class="eng-hub-list-row__secondary">${dt}</span>
			</div>
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">📏</span>
				${__("Medições")}
				<span class="eng-hub-panel__count">${measurements.length}</span>
			</h3>
		</div>
		${rows}
	</div>`);

	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_timelogs(frm, timelogs) {
	const $w = frm.fields_dict.timelogs_panel?.$wrapper;
	if (!$w) return;

	if (!timelogs.length) {
		$w.html(_eng_hub_empty("⏱️", __("Nenhum registro de horas"), __("+ Horas"), "new-timelog"));
		$w.find('[data-hub-action="new-timelog"]').on("click", () => {
			frappe.new_doc("Time Log", { project: frm.doc.name });
		});
		return;
	}

	const total = timelogs.reduce((sum, row) => sum + (row.duration_hours || 0), 0);
	const rows = timelogs
		.slice(0, 8)
		.map((timelog) => {
			const dt = timelog.log_date ? frappe.datetime.str_to_user(timelog.log_date) : "";
			return `<div class="eng-hub-list-row" data-route="Form/Time Log/${frappe.utils.escape_html(
				timelog.name
			)}">
			<div class="eng-hub-list-row__icon">⏱️</div>
			<div class="eng-hub-list-row__main">
				${frappe.utils.escape_html(timelog.activity || "")}
				<span class="eng-hub-list-row__secondary">${dt}</span>
			</div>
			<div class="eng-hub-list-row__value">${(timelog.duration_hours || 0).toFixed(1)}h</div>
		</div>`;
		})
		.join("");

	const seeAll =
		timelogs.length > 8
			? `<div style="text-align:center;padding:10px 0">
			<a style="font-size:var(--text-xs);color:var(--primary);cursor:pointer" data-hub-action="list-timelogs">
				${__("Ver todos")} →
			</a>
		</div>`
			: "";

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">⏱️</span>
				${__("Horas Trabalhadas")}
			</h3>
			<div style="font-size:var(--text-sm);color:var(--text-muted)">
				${__("Total")}: <strong style="color:var(--text-color)">${total.toFixed(1)}h</strong>
			</div>
		</div>
		${rows}
		${seeAll}
	</div>`);

	$w.find('[data-hub-action="new-timelog"]').on("click", () => {
		frappe.new_doc("Time Log", { project: frm.doc.name });
	});
	$w.find('[data-hub-action="list-timelogs"]').on("click", () => {
		frappe.set_route("List", "Time Log", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function _eng_hub_empty(icon, msg, btnLabel, actionName) {
	return `<div class="eng-hub-empty">
		<div class="eng-hub-empty__icon">${icon}</div>
		<div>${msg}</div>
		<button type="button" class="eng-hub-empty__action" data-hub-action="${actionName}">${btnLabel}</button>
	</div>`;
}

function _eng_hub_status_badge(status) {
	const map = {
		Pago: "green",
		Recebido: "green",
		Received: "green",
		Vencida: "red",
		Vencido: "red",
		Overdue: "red",
		Atrasado: "red",
		"A vencer": "orange",
		Pending: "orange",
		Pendente: "orange",
		"Em aberto": "blue",
		Open: "blue",
	};
	return `<span class="eng-hub-badge eng-hub-badge--${
		map[status] || "gray"
	}" style="margin-left:8px">${status || ""}</span>`;
}
