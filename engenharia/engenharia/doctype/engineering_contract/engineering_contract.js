frappe.ui.form.on("Engineering Contract", {
	refresh(frm) {
		sum_installments(frm);

		if (!frm.is_new()) {
			frm.add_custom_button(__("Re-sincronizar Pagamentos"), () => {
				frappe.confirm(
					__(
						"Isso vai re-sincronizar todos os pagamentos com as parcelas atuais. Continuar?"
					),
					() => {
						frappe.call({
							method: "engenharia.financial.resync_contract_payments",
							args: { contract_name: frm.doc.name },
							freeze: true,
							freeze_message: __("Sincronizando..."),
							callback(r) {
								if (r.message && r.message.status === "ok") {
									frm.reload_doc();
								}
							},
						});
					}
				);
			}).addClass("btn-primary-dark");
		}
	},
	base_value(frm) {
		calculate_installment_value(frm);
	},
	installment_count(frm) {
		calculate_installment_value(frm);
	},
	generate_installments(frm) {
		generate_installment_table(frm);
	},
	apply_amendment(frm) {
		if (frm.is_new()) {
			frappe.msgprint(__("Salve o contrato antes de aplicar aditivos."));
			return;
		}
		const d = new frappe.ui.Dialog({
			title: __("Aplicar Aditivo"),
			fields: [
				{
					fieldtype: "HTML",
					options: `<p>${__(
						"Escolha como aplicar os aditivos registrados na tabela."
					)}</p>`,
				},
			],
			primary_action_label: __("Regenerar parcelas futuras"),
			primary_action() {
				call_apply_amendment(frm, 1);
				d.hide();
			},
		});
		d.set_secondary_action_label(__("Somente registrar histórico"));
		d.set_secondary_action(() => {
			call_apply_amendment(frm, 0);
			d.hide();
		});
		d.show();
	},
});

frappe.ui.form.on("Engineering Contract Installment", {
	payment_condition(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.payment_condition && row.payment_condition !== "Data fixa") {
			frappe.model.set_value(cdt, cdn, "due_date", null);
		}
	},
	amount(frm) {
		sum_installments(frm);
	},
	installments_remove(frm) {
		sum_installments(frm);
	},
	installments_add(frm) {
		sum_installments(frm);
	},
});

frappe.ui.form.on("Engineering Contract Amendment", {
	amount(frm) {
		calculate_installment_value(frm);
	},
	amendments_remove(frm) {
		calculate_installment_value(frm);
	},
});

function calculate_installment_value(frm) {
	const base = flt(frm.doc.base_value);
	let additions = 0;
	let reductions = 0;
	(frm.doc.amendments || []).forEach((row) => {
		if (row.amendment_type === "Adição") {
			additions += flt(row.amount);
		} else if (row.amendment_type === "Redução") {
			reductions += flt(row.amount);
		}
	});
	const current = base + additions - reductions;
	frm.set_value("current_value", current);
	const count = flt(frm.doc.installment_count);
	if (count > 0 && current > 0) {
		frm.set_value("installment_value", current / count);
	}
}

function generate_installment_table(frm) {
	const count = flt(frm.doc.installment_count);
	const startDate = frm.doc.first_installment_date;
	const total = flt(frm.doc.current_value);

	if (!count || count <= 0) {
		frappe.msgprint(__("Preencha o número de parcelas."));
		return;
	}
	if (!startDate) {
		frappe.msgprint(__("Preencha a data da primeira parcela."));
		return;
	}
	if (!total) {
		frappe.msgprint(__("Preencha o valor base do contrato."));
		return;
	}

	const amount = total / count;
	frm.clear_table("installments");
	for (let i = 0; i < count; i++) {
		const row = frm.add_child("installments");
		row.due_date = frappe.datetime.add_months(startDate, i);
		row.payment_condition = "Data fixa";
		row.amount = amount;
		row.status = "Pendente";
		row.description = __("Parcela {0} de {1}", [i + 1, count]);
	}
	frm.refresh_field("installments");
	sum_installments(frm);
	frappe.msgprint(__("{0} parcelas geradas com sucesso!", [count]));
}

function sum_installments(frm) {
	let total = 0;
	(frm.doc.installments || []).forEach((row) => {
		total += flt(row.amount);
	});
	if (total && !flt(frm.doc.current_value)) {
		frm.set_value("current_value", total);
	}
}

function call_apply_amendment(frm, regenerate) {
	frm.save().then(() => {
		frappe.call({
			method:
				"engenharia.engenharia.doctype.engineering_contract.engineering_contract.apply_amendment",
			args: {
				contract_name: frm.doc.name,
				regenerate,
			},
			freeze: true,
			callback() {
				frm.reload_doc();
			},
		});
	});
}
