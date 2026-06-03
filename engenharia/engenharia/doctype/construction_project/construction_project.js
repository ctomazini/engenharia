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
		}
	},
});

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
