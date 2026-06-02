frappe.ui.form.on("Construction Project", {
	refresh(frm) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.bindMask(frm, "address_cep", EngenhariaMasks.applyCEP, "cep");
		}
	},
});
