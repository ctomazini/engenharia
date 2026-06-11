frappe.listview_settings["Customer"] = {
	...(frappe.listview_settings["Customer"] || {}),
	hide_name_column: true,
	formatters: {
		cpf(value) {
			return window.EngenhariaMasks
				? EngenhariaMasks.listFormatters.cpf(value)
				: value || "";
		},
		cnpj(value) {
			return window.EngenhariaMasks
				? EngenhariaMasks.listFormatters.cnpj(value)
				: value || "";
		},
		person_type(value, _df, doc) {
			const tipo = frappe.utils.escape_html(value || "");
			const id = frappe.utils.escape_html(doc.name || "");
			const badge = id
				? `<span class="indicator-pill gray ellipsis" style="max-width: 130px; margin-right: 6px;">${id}</span>`
				: "";

			return `${badge}<span>${tipo}</span>`;
		},
	},
};
