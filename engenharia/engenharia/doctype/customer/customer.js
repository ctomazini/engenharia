frappe.ui.form.on("Customer", {
	refresh(frm) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.setupCustomerForm(frm);
		}
	},
	person_type(frm) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.setupCustomerForm(frm);
		}
	},
	cpf(frm) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.formatFormField(frm, "cpf", EngenhariaMasks.applyCPF);
		}
	},
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
