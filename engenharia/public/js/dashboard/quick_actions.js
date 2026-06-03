frappe.provide("engenharia.dashboard");

engenharia.dashboard.quick_actions = {
	actions() {
		return [
			{ label: __("Cliente"), icon: "user-plus", doctype: "Customer" },
			{ label: __("Obra"), icon: "folder-plus", doctype: "Construction Project" },
			{ label: __("Contrato"), icon: "file-plus", doctype: "Engineering Contract" },
			{ label: __("Pagamento"), icon: "circle-dollar-sign", doctype: "Payment" },
			{ label: __("Custo de obra"), icon: "receipt", doctype: "Work Cost" },
			{ label: __("Despesa reembolsável"), icon: "wallet", doctype: "Reimbursable Expense" },
			{ label: __("Prazo"), icon: "clock-plus", doctype: "Deadline" },
			{ label: __("Protocolo"), icon: "file-check", doctype: "Permit" },
			{ label: __("Comunicação"), icon: "message-square-plus", doctype: "Communication Log" },
			{ label: __("Tarefa"), icon: "list-plus", doctype: "Task" },
			{ label: __("Horas"), icon: "clock", doctype: "Time Log" },
		];
	},

	icon(name) {
		try {
			return frappe.utils.icon(name, "sm") || "";
		} catch (e) {
			return "";
		}
	},

	render(container) {
		const chips = this.actions()
			.map(
				(action) => `
			<button type="button" class="eng-dash-action-chip" data-new-dt="${frappe.utils.escape_html(action.doctype)}">
				${this.icon(action.icon)}
				<span>${frappe.utils.escape_html(action.label)}</span>
			</button>`
			)
			.join("");

		container.html(`
			<div class="eng-dash-actions-wrap">
				<p class="eng-dash-actions-label">${__("Ações rápidas")}</p>
				<div class="eng-dash-actions">${chips}</div>
			</div>
		`);
	},

	bind($root) {
		$root.find(".eng-dash-action-chip").on("click", function () {
			const dt = $(this).attr("data-new-dt");
			if (dt) frappe.new_doc(dt);
		});
	},
};
