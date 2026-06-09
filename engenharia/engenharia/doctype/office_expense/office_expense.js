frappe.ui.form.on("Office Expense", {
	refresh(frm) {
		if (frm.doc.status === "Atrasado") {
			frm.dashboard.set_headline(
				__('<span style="color:var(--red-500)">⚠ Despesa atrasada!</span>')
			);
		}
		if (frm.doc.status === "Pago") {
			frm.page.set_indicator(__("Pago"), "green");
		}

		if (frm.doc.is_recurring && !frm.is_new() && frm.doc.next_due_date) {
			frm.add_custom_button(
				__("Gerar Próxima"),
				() => {
					frappe.call({
						method:
							"engenharia.engenharia.doctype.office_expense.office_expense.create_next_office_expense",
						args: { source_name: frm.doc.name },
						callback(r) {
							if (r.message) {
								frappe.set_route("Form", "Office Expense", r.message);
							}
						},
					});
				},
				__("Ações")
			);
		}
	},

	payment_date(frm) {
		if (frm.doc.payment_date) {
			frm.set_value("status", "Pago");
		}
	},
});
