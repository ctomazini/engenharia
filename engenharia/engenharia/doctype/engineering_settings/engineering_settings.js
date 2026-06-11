frappe.ui.form.on("Engineering Settings", {
	refresh(frm) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.setupEngineeringSettingsForm(frm);
		}
	},
	company_cnpj(frm) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.formatFormField(frm, "company_cnpj", EngenhariaMasks.applyCNPJ);
		}
	},
	engineer_cpf(frm) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.formatFormField(frm, "engineer_cpf", EngenhariaMasks.applyCPF);
		}
	},
	engineer_phone(frm) {
		if (window.EngenhariaMasks) {
			EngenhariaMasks.formatFormField(frm, "engineer_phone", EngenhariaMasks.applyPhone);
		}
	},
});
