frappe.ui.form.on("Work Cost", {
	refresh(frm) {
		const clientFunded = frm.doc.funded_by === "Cliente";
		frm.toggle_reqd("payment_method", !clientFunded);
		if (clientFunded) {
			frm.set_df_property(
				"funded_by",
				"description",
				__("O cliente paga direto — este lançamento não entra no fluxo de caixa do escritório.")
			);
		}
	},
});
