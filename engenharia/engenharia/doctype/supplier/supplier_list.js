frappe.listview_settings["Supplier"] = {
	...(frappe.listview_settings["Supplier"] || {}),
	formatters: {
		cnpj(value) {
			return window.EngenhariaMasks
				? EngenhariaMasks.listFormatters.cnpj(value)
				: value || "";
		},
		phone(value) {
			return window.EngenhariaMasks
				? EngenhariaMasks.listFormatters.phone(value)
				: value || "";
		},
	},
};
