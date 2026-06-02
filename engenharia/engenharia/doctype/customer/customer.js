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
	legal_representative_cpf(frm) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.formatFormField(
				frm,
				"legal_representative_cpf",
				EngenhariaMasks.applyCPF
			);
		}
	},
});

frappe.ui.form.on("Customer Contact", {
	form_render(frm) {
		if (!window.EngenhariaMasks) return;
		EngenhariaMasks.bindMask(frm, "phone", EngenhariaMasks.applyPhone, "fixo");
		EngenhariaMasks.bindMask(frm, "mobile", EngenhariaMasks.applyPhone, "celular");
	},
	phone(frm, cdt, cdn) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.formatChildField(cdt, cdn, "phone", EngenhariaMasks.applyPhone);
		}
	},
	mobile(frm, cdt, cdn) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.formatChildField(cdt, cdn, "mobile", EngenhariaMasks.applyPhone);
		}
	},
});

frappe.ui.form.on("Customer Address", {
	form_render(frm) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.bindMask(frm, "cep", EngenhariaMasks.applyCEP, "cep");
		}
	},
	cep(frm, cdt, cdn) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.formatChildField(cdt, cdn, "cep", EngenhariaMasks.applyCEP);
		}
	},
});
