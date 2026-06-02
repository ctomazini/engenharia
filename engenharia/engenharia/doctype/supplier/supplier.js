frappe.ui.form.on("Supplier", {
	cnpj(frm) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.formatFormField(frm, "cnpj", EngenhariaMasks.applyCNPJ);
		}
	},
	phone(frm) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.formatFormField(frm, "phone", EngenhariaMasks.applyPhone);
		}
	},
});
