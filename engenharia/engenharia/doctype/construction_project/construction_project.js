frappe.ui.form.on("Construction Project", {
	refresh(frm) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.bindMask(frm, "address_cep", EngenhariaMasks.applyCEP, "cep");
		}

		frm.add_custom_button(__("Adicionar especificação"), () => eng_add_project_item(frm), __(
			"Especificações Técnicas"
		));

		if (!frm.is_new()) {
			eng_refresh_spec_rollup(frm);
			eng_refresh_spec_items_summary(frm);
			eng_refresh_commission_summary(frm);
			eng_add_hub_create_buttons(frm);
			frm.add_custom_button(
				__("Redistribuir Pesos"),
				function () {
					frappe.call({
						method: "engenharia.stage_template.redistribute_stage_weights",
						args: { project: frm.doc.name },
						freeze: true,
						callback(r) {
							if (r.message && r.message.count) {
								frappe.show_alert({
									message: __("{0} etapas redistribuídas", [r.message.count]),
									indicator: "green",
								});
								frm.reload_doc();
							}
						},
					});
				},
				__("Etapas")
			);
			frm.add_custom_button(
				__("Nova revisão de orçamento"),
				() => eng_create_budget_revision(frm),
				__("Orçamento")
			);
			frm.add_custom_button(__("Gerar Documentos"), () => eng_open_generate_documents_dialog(frm), __(
				"Documentos"
			));

			eng_hub_load(frm);

			if (frm.fields_dict.spec_items_summary_panel) {
				frm.fields_dict.spec_items_summary_panel.$wrapper
					.off("click", ".eng-spec-refresh")
					.on("click", ".eng-spec-refresh", () => {
						eng_refresh_spec_items_summary(frm);
						eng_refresh_spec_rollup(frm);
					});
				frm.fields_dict.spec_items_summary_panel.$wrapper
					.off("click", ".eng-spec-row")
					.on("click", ".eng-spec-row", function () {
						const name = $(this).attr("data-name");
						if (name) {
							frappe.set_route("Form", "Project Item", name);
						}
					});
			}
		}
	},
	project_type(frm) {
		if (!frm.doc.project_type || frm.is_new()) return;
		frappe.call({
			method: "engenharia.stage_template.get_stage_count_for_project",
			args: { project: frm.doc.name },
			callback(r) {
				const count = r.message || 0;
				if (count > 0) {
					frappe.confirm(
						__(
							"Esta obra já possui {0} etapa(s). Substituir pelas etapas do template?",
							[count]
						),
						() => eng_apply_stage_template(frm)
					);
				} else {
					eng_apply_stage_template(frm);
				}
			},
		});
	},
});

function eng_apply_stage_template(frm) {
	frappe.call({
		method: "engenharia.stage_template.apply_template_to_project",
		args: {
			project: frm.doc.name,
			project_type: frm.doc.project_type,
		},
		freeze: true,
		freeze_message: __("Criando etapas..."),
		callback(r) {
			if (r.message && r.message.created) {
				frappe.show_alert({
					message: __("{0} etapa(s) criada(s)", [r.message.created]),
					indicator: "green",
				});
				frm.reload_doc();
			}
		},
	});
}

function eng_hub_defaults(frm) {
	return {
		project: frm.doc.name,
		customer: frm.doc.customer,
	};
}

function eng_add_hub_create_buttons(frm) {
	const hub = eng_hub_defaults(frm);

	frm.add_custom_button(__("+ Contrato"), () => frappe.new_doc("Engineering Contract", hub), __("Criar"));
	frm.add_custom_button(__("+ Pagamento"), () => frappe.new_doc("Payment", hub), __("Criar"));
	frm.add_custom_button(__("+ Custo"), () => frappe.new_doc("Work Cost", { project: hub.project }), __("Criar"));
	frm.add_custom_button(
		__("+ Despesa reembolsável"),
		() => frappe.new_doc("Reimbursable Expense", hub),
		__("Criar")
	);
	frm.add_custom_button(__("+ Prazo"), () => frappe.new_doc("Deadline", hub), __("Criar"));
	frm.add_custom_button(__("+ Protocolo"), () => frappe.new_doc("Permit", hub), __("Criar"));
	frm.add_custom_button(__("+ Tarefa"), () => frappe.new_doc("Task", hub), __("Criar"));
	frm.add_custom_button(__("+ Comunicação"), () => frappe.new_doc("Communication Log", hub), __("Criar"));
	frm.add_custom_button(__("+ Horas"), () => frappe.new_doc("Time Log", hub), __("Criar"));
	frm.add_custom_button(
		__("+ Etapa"),
		() => frappe.new_doc("Project Stage", { project: hub.project }),
		__("Criar")
	);
}

function eng_create_budget_revision(frm) {
	frappe.confirm(
		__(
			"Criar nova revisão de orçamento? A revisão vigente será arquivada com o total atual e uma nova revisão vazia será aberta."
		),
		() => {
			frappe.call({
				method: "engenharia.engenharia.doctype.construction_project.construction_project.create_budget_revision",
				args: { project: frm.doc.name },
				freeze: true,
				freeze_message: __("Criando revisão..."),
				callback(r) {
					const data = r.message || {};
					if (data.revision_number) {
						frappe.show_alert({
							message: __("Revisão {0} criada", [data.revision_number]),
							indicator: "green",
						});
						frm.reload_doc();
					}
				},
			});
		}
	);
}

function eng_refresh_spec_rollup(frm) {
	frappe.call({
		method: "engenharia.project_rollup.get_construction_project_spec_preview",
		args: { project: frm.doc.name },
		callback(r) {
			const data = r.message || {};
			if (frm.fields_dict.spec_preview_panel) {
				const preview = data.preview_html || `<p class="text-muted">${__(
					"Nenhum resultado com papel Prévia."
				)}</p>`;
				frm.fields_dict.spec_preview_panel.$wrapper.html(preview);
			}
			if (data.project_total != null) {
				frm.set_value("spec_project_total", data.project_total);
			}
		},
	});
}

function eng_refresh_spec_items_summary(frm) {
	if (!frm.fields_dict.spec_items_summary_panel) {
		return;
	}

	frappe.call({
		method: "engenharia.project_rollup.get_project_items_summary",
		args: { project: frm.doc.name },
		callback(r) {
			const data = r.message || {};
			const items = data.items || [];
			const $panel = frm.fields_dict.spec_items_summary_panel.$wrapper;
			$panel.html(eng_render_spec_items_table(frm, items, data.project_total));
		},
	});
}

function eng_render_spec_items_table(frm, items, projectTotal) {
	const fmt = (value) => format_currency(value || 0, frappe.defaults.get_default("currency") || "BRL");

	let html = `
		<div class="eng-spec-summary">
			<div class="d-flex justify-content-between align-items-center mb-2">
				<strong>${__("Especificações da Obra")}</strong>
				<button type="button" class="btn btn-xs btn-default eng-spec-refresh">${__("Atualizar")}</button>
			</div>`;

	if (!items.length) {
		html += `<p class="text-muted">${__("Nenhum item técnico vinculado a esta obra.")}</p></div>`;
		return html;
	}

	html += `
		<div class="table-responsive">
			<table class="table table-bordered table-sm eng-spec-summary-table">
				<thead>
					<tr>
						<th>${__("Item")}</th>
						<th>${__("Qtd")}</th>
						<th>${__("Unid")}</th>
						<th>${__("Parâmetros")}</th>
						<th class="text-right">${__("Valor Unit.")}</th>
						<th class="text-right">${__("Total")}</th>
					</tr>
				</thead>
				<tbody>`;

	items.forEach((item) => {
		const label = frappe.utils.escape_html(item.instance_label || item.technical_item || item.title);
		const params = frappe.utils.escape_html(
			[item.params_summary, item.outputs_summary].filter(Boolean).join(" · ")
		);
		html += `
			<tr class="eng-spec-row" data-name="${frappe.utils.escape_html(item.name)}">
				<td>${label}</td>
				<td>${frappe.utils.escape_html(String(item.quantity || 1))}</td>
				<td>${frappe.utils.escape_html(item.unit || "")}</td>
				<td class="text-muted small">${params || "—"}</td>
				<td class="text-right">${item.unit_price ? fmt(item.unit_price) : "—"}</td>
				<td class="text-right">${fmt(item.total_value)}</td>
			</tr>`;
	});

	html += `
				</tbody>
				<tfoot>
					<tr>
						<th colspan="5" class="text-right">${__("TOTAL OBRA")}</th>
						<th class="text-right">${fmt(projectTotal)}</th>
					</tr>
				</tfoot>
			</table>
		</div>
	</div>`;

	return html;
}

function eng_refresh_commission_summary(frm) {
	if (!frm.fields_dict.commission_summary_panel) {
		return;
	}

	frappe.call({
		method: "engenharia.project_rollup.get_project_commission_summary",
		args: { project: frm.doc.name },
		callback(r) {
			const data = r.message || {};
			const $panel = frm.fields_dict.commission_summary_panel.$wrapper;
			if (!data.count) {
				$panel.html(`<p class="text-muted">${__("Nenhuma comissão vinculada a esta obra.")}</p>`);
				return;
			}
			const fmt = (value) =>
				format_currency(value || 0, frappe.defaults.get_default("currency") || "BRL");
			const activeLabel =
				data.active_count === 1
					? __("1 comissão ativa")
					: __("{0} comissões ativas", [data.active_count]);
			$panel.html(`
				<div class="eng-commission-summary">
					<a href="#" class="eng-commission-link">
						${__(
							"Comissões: {0} recebido de {1} ({2})",
							[fmt(data.total_paid), fmt(data.total_value), activeLabel]
						)}
					</a>
				</div>`);
			$panel.find(".eng-commission-link").on("click", (e) => {
				e.preventDefault();
				frappe.set_route("List", "Commission", {
					construction_project: frm.doc.name,
				});
			});
		},
	});
}

function eng_add_project_item(frm) {
	if (frm.is_new()) {
		frappe.msgprint({
			title: __("Salve a obra"),
			message: __("Salve a obra antes de adicionar itens técnicos."),
			indicator: "orange",
		});
		return;
	}

	frappe.call({
		method: "engenharia.engenharia.doctype.construction_project.construction_project.get_technical_items_for_select",
		callback(r) {
			const items = r.message || [];
			if (!items.length) {
				frappe.msgprint({
					title: __("Sem itens técnicos"),
					message: __(
						"Cadastre modelos em <b>Itens Técnicos</b> ou execute <code>bench migrate</code>."
					),
					indicator: "orange",
				});
				return;
			}
			eng_show_project_item_dialog(frm, items);
		},
	});
}

function eng_show_project_item_dialog(frm, items) {
	const d = new frappe.ui.Dialog({
		title: __("Adicionar especificação técnica"),
		fields: [
			{
				fieldname: "help",
				fieldtype: "HTML",
				options: `<p class="text-muted small">${__(
					"Selecione o modelo. Um formulário de item será aberto para preencher parâmetros e ver resultados calculados."
				)}</p>`,
			},
			{
				fieldname: "technical_item",
				fieldtype: "Select",
				label: __("Modelo"),
				options: items.map((item) => item.name).join("\n"),
				reqd: 1,
			},
			{
				fieldname: "instance_label",
				fieldtype: "Data",
				label: __("Identificação"),
				description: __("Ex.: Fossa social, Caixa superior, PAV-01"),
			},
			{
				fieldname: "stage",
				fieldtype: "Link",
				label: __("Etapa / Pavimento"),
				options: "Project Stage",
				only_select: 1,
				filters: { project: frm.doc.name },
			},
		],
		primary_action_label: __("Adicionar"),
		primary_action(values) {
			const btn = d.get_primary_btn();
			btn.prop("disabled", true);

			frappe.call({
				method: "engenharia.engenharia.doctype.construction_project.construction_project.create_project_item",
				args: {
					project: frm.doc.name,
					technical_item: values.technical_item,
					instance_label: values.instance_label,
					stage: values.stage,
				},
				callback(r) {
					d.hide();
					if (r.message) {
						frappe.set_route("Form", "Project Item", r.message);
					}
				},
				error() {
					btn.prop("disabled", false);
				},
			});
		},
	});

	d.show();
}

function eng_open_generate_documents_dialog(frm) {
	frappe.call({
		method: "engenharia.documents.get_available_templates",
		callback(r_templates) {
			const templates = r_templates.message || [];
			if (!templates.length) {
				frappe.msgprint(
					__(
						"Nenhum template cadastrado. Vá em Template de Documento para cadastrar."
					)
				);
				return;
			}

			frappe.call({
				method: "engenharia.documents.get_available_kits",
				callback(r_kits) {
					eng_mount_generate_documents_dialog(frm, templates, r_kits.message || []);
				},
			});
		},
	});
}

function eng_mount_generate_documents_dialog(frm, templates, kits) {
	const grouped = {};
	templates.forEach((tpl) => {
		const doc_type = tpl.document_type || __("Outro");
		if (!grouped[doc_type]) {
			grouped[doc_type] = [];
		}
		grouped[doc_type].push(tpl);
	});

	let checklist_html =
		'<div class="eng-doc-bulk-list" style="max-height:320px;overflow-y:auto;">';
	checklist_html +=
		'<p class="text-muted small">' +
		__("Selecione os templates ou use um kit para pré-marcar.") +
		"</p>";
	checklist_html +=
		'<p><label class="checkbox"><input type="checkbox" class="eng-doc-select-all"> ' +
		__("Selecionar todos") +
		"</label></p>";

	Object.keys(grouped)
		.sort()
		.forEach((doc_type) => {
			checklist_html +=
				'<div style="margin-top:10px;font-weight:600;">' +
				frappe.utils.escape_html(doc_type) +
				"</div>";
			grouped[doc_type].forEach((tpl) => {
				const label = tpl.template_name || tpl.name;
				checklist_html +=
					'<p style="margin:4px 0 4px 12px;">' +
					'<label class="checkbox">' +
					'<input type="checkbox" class="eng-doc-template" data-template="' +
					frappe.utils.escape_html(tpl.name) +
					'"> ' +
					frappe.utils.escape_html(label) +
					"</label></p>";
			});
		});
	checklist_html += "</div>";

	const dialog = new frappe.ui.Dialog({
		title: __("Gerar Documentos"),
		fields: [
			{
				fieldname: "kit",
				fieldtype: "Select",
				label: __("Kit (opcional)"),
				options: ["", ...kits.map((k) => k.name)],
				description: __("Pré-seleciona os templates de um kit"),
			},
			{
				fieldname: "templates_html",
				fieldtype: "HTML",
				options: checklist_html,
			},
		],
		primary_action_label: __("Gerar documentos"),
		primary_action() {
			const selected = [];
			dialog.$wrapper.find(".eng-doc-template:checked").each(function () {
				selected.push($(this).attr("data-template"));
			});
			if (!selected.length) {
				frappe.msgprint(__("Selecione ao menos um template."));
				return;
			}
			dialog.hide();
			eng_generate_documents_batch(frm, selected);
		},
	});

	dialog.show();

	if (dialog.fields_dict.kit && kits.length) {
		dialog.fields_dict.kit.df.options = ["", ...kits.map((k) => k.name)];
		dialog.fields_dict.kit.refresh();
		dialog.fields_dict.kit.$input.on("change", function () {
			const kit_name = dialog.get_value("kit");
			dialog.$wrapper.find(".eng-doc-template").prop("checked", false);
			if (!kit_name) {
				eng_update_bulk_dialog_primary_action(dialog);
				return;
			}
			const kit = kits.find((k) => k.name === kit_name);
			if (!kit || !kit.templates) {
				return;
			}
			kit.templates.forEach((template_name) => {
				dialog.$wrapper
					.find('.eng-doc-template[data-template="' + template_name + '"]')
					.prop("checked", true);
			});
			eng_update_bulk_dialog_primary_action(dialog);
		});
	} else if (dialog.fields_dict.kit) {
		dialog.toggle_display("kit", false);
	}

	dialog.$wrapper.find(".eng-doc-select-all").on("change", function () {
		const checked = $(this).is(":checked");
		dialog.$wrapper.find(".eng-doc-template").prop("checked", checked);
		eng_update_bulk_dialog_primary_action(dialog);
	});

	dialog.$wrapper.on("change", ".eng-doc-template", function () {
		eng_update_bulk_dialog_primary_action(dialog);
	});

	eng_update_bulk_dialog_primary_action(dialog);
}

function eng_update_bulk_dialog_primary_action(dialog) {
	const total = dialog.$wrapper.find(".eng-doc-template:checked").length;
	dialog.set_primary_action(
		total ? __("Gerar {0} documento(s)", [total]) : __("Gerar documentos")
	);
}

function eng_generate_documents_batch(frm, template_names) {
	frappe.call({
		method: "engenharia.documents.generate_project_documents",
		args: {
			project_name: frm.doc.name,
			template_names,
		},
		freeze: true,
		freeze_message: __("Gerando documentos..."),
		callback(r) {
			const data = r.message;
			if (!data) {
				return;
			}
			let html = "";

			if (data.generated && data.generated.length) {
				html += "<p><strong>" + __("Documentos gerados:") + "</strong></p><ul>";
				data.generated.forEach((item) => {
					html +=
						"<li>" +
						frappe.utils.escape_html(item.title || item.template) +
						' — <a href="' +
						item.file_url +
						'" target="_blank">' +
						frappe.utils.escape_html(item.file_name) +
						"</a></li>";
				});
				html += "</ul>";
			}

			if (data.failures && data.failures.length) {
				html += "<p><strong>" + __("Falhas:") + "</strong></p><ul>";
				data.failures.forEach((item) => {
					html +=
						"<li>" +
						frappe.utils.escape_html(item.template) +
						": " +
						frappe.utils.escape_html(item.error) +
						"</li>";
				});
				html += "</ul>";
			}

			frappe.msgprint({
				title: __("Geração em lote"),
				message: html || __("Nenhum documento gerado."),
				indicator: data.failures && data.failures.length ? "orange" : "green",
				wide: true,
			});
			frm.reload_doc();
		},
	});
}
