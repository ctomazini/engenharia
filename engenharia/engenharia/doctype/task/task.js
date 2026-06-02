frappe.ui.form.on("Task", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.status === "Feito" || frm.doc.status === "Cancelada") {
			return;
		}
		frm.add_custom_button(__("Concluir"), () => {
			frappe.call({
				method: "complete",
				doc: frm.doc,
				callback() {
					frm.reload_doc();
				},
			});
		});
	},
});
