frappe.ui.form.on("Document Template", {
	view_placeholders(frm) {
		frappe.call({
			method: "engenharia.documents.get_placeholder_reference",
			freeze: true,
			freeze_message: __("Carregando placeholders..."),
			callback(r) {
				if (!r.message) {
					return;
				}
				eng_render_placeholder_reference(r.message);
			},
		});
	},
});
