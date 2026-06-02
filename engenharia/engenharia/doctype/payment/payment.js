frappe.ui.form.on("Payment", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.status === "Cancelado") {
			return;
		}
		if (frm.doc.origin_type === "Parcela do Contrato" && frm.doc.status === "Pendente") {
			frm.add_custom_button(__("Cancelar Pagamento"), () => {
				frappe.confirm(__("Cancelar este pagamento?"), () => {
					frappe.call({
						method: "engenharia.financial.cancel_contract_payment",
						args: { payment_name: frm.doc.name },
						callback() {
							frm.reload_doc();
						},
					});
				});
			});
		}
	},
});
