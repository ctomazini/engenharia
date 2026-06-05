frappe.ui.form.on("Project Item", {
	refresh(frm) {
		eng_toggle_pricing_sections(frm);

		if (frm.doc.pricing_mode === "Fórmula" && frm.doc.technical_item && !frm.doc.parameter_values?.length) {
			eng_sync_parameters(frm, false);
		}

		if (frm.doc.technical_item && frm.doc.pricing_mode !== "Preço unitário" && !frm.is_new()) {
			frm.add_custom_button(__("Recarregar parâmetros"), () => eng_sync_parameters(frm, true), __(
				"Parâmetros"
			));
		}
	},

	pricing_mode(frm) {
		eng_toggle_pricing_sections(frm);
	},

	technical_item(frm) {
		if (frm.doc.pricing_mode === "Preço unitário") {
			return;
		}
		eng_sync_parameters(frm, true);
	},
});

function eng_toggle_pricing_sections(frm) {
	const mode = frm.doc.pricing_mode || "Fórmula";
	const showParams = mode === "Fórmula" || mode === "Composição de custos";
	const showUnitPrice = mode === "Preço unitário";
	const showComposition = mode === "Composição de custos";

	["sec_parameters", "parameter_values", "sec_results", "computed_outputs"].forEach((fieldname) => {
		frm.toggle_display(fieldname, showParams);
	});
	frm.toggle_display("sec_unit_price", showUnitPrice);
	frm.toggle_display("unit_price", showUnitPrice);
	frm.toggle_display("sec_cost_composition", showComposition);
	frm.toggle_display("cost_components", showComposition);
}

function eng_sync_parameters(frm, confirm_replace) {
	if (!frm.doc.technical_item) {
		return;
	}

	const apply_rows = (rows) => {
		frm.clear_table("parameter_values");
		(rows || []).forEach((row) => {
			const child = frm.add_child("parameter_values");
			child.field_key = row.field_key;
			child.label = row.label;
			child.value = row.value || "";
			child.unit = row.unit;
			child.data_type = row.data_type;
			child.required = row.required;
		});
		frm.refresh_field("parameter_values");
	};

	const load = () => {
		frappe.call({
			method: "engenharia.engenharia.doctype.project_item.project_item.get_parameter_template",
			args: { technical_item: frm.doc.technical_item },
			callback(r) {
				apply_rows(r.message || []);
				if ((r.message || []).length) {
					frappe.show_alert({
						message: __(
							"{0} parâmetros carregados do modelo. Preencha a coluna Valor.",
							[r.message.length]
						),
						indicator: "green",
					});
				}
			},
		});
	};

	if (confirm_replace && frm.doc.parameter_values?.length) {
		frappe.confirm(
			__(
				"Substituir os parâmetros atuais pelos definidos no item técnico? Valores digitados serão perdidos."
			),
			load
		);
		return;
	}

	load();
}
