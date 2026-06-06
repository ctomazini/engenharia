const ENG_OUTPUT_ROLE_DESCRIPTIONS = {
	"": __("Output calculado sem função automática."),
	value: __("Define o valor monetário (R$) do item. Usado no orçamento da obra."),
	volume: __("Volume calculado (m³). Aparece no título e resumo do item."),
	area: __("Área calculada (m²). Aparece no título e resumo do item."),
	preview: __("Informação complementar exibida em resumos e listas."),
};

frappe.ui.form.on("Technical Item", {
	refresh(frm) {
		eng_set_output_role_descriptions(frm);
	},
});

frappe.ui.form.on("Technical Item Output", {
	role(frm, cdt, cdn) {
		eng_set_output_role_description_for_row(frm, cdt, cdn);
	},
	outputs_add(frm, cdt, cdn) {
		eng_set_output_role_description_for_row(frm, cdt, cdn);
	},
});

function eng_set_output_role_descriptions(frm) {
	(frm.doc.outputs || []).forEach((row) => {
		eng_set_output_role_description_for_row(frm, row.doctype, row.name);
	});
}

function eng_set_output_role_description_for_row(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	if (!row || !frm.fields_dict.outputs) {
		return;
	}
	const grid = frm.fields_dict.outputs.grid;
	const gridRow = grid.grid_rows_by_docname?.[cdn];
	const desc = ENG_OUTPUT_ROLE_DESCRIPTIONS[row.role || ""] || "";
	if (gridRow?.columns?.role) {
		gridRow.columns.role.field.df.description = desc;
		if (gridRow.columns.role.field.$wrapper) {
			gridRow.columns.role.field.set_description(desc);
		}
	}
}
