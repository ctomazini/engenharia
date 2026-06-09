frappe.provide("engenharia.dashboard");

engenharia.dashboard.quick_actions = {
	/** Ordem: Dia a Dia (sidebar) → financeiro frequente. Sem contrato/protocolo/reembolso — cadastro episódico. */
	actions() {
		return [
			{ label: __("Cliente"), icon: "user-plus", doctype: "Customer" },
			{ label: __("Obra"), icon: "folder-plus", doctype: "Construction Project" },
			{ label: __("Prazo"), icon: "clock-plus", doctype: "Deadline" },
			{ label: __("Tarefa"), icon: "list-plus", doctype: "Task" },
			{
				label: __("Calendário"),
				icon: "calendar",
				route: ["List", "Event", "Calendar"],
				read_doctype: "Event",
			},
			{ label: __("Comunicação"), icon: "message-square-plus", doctype: "Communication Log" },
			{ label: __("Horas"), icon: "clock", doctype: "Time Log" },
			{ label: __("Recebimento"), icon: "circle-dollar-sign", doctype: "Payment" },
			{ label: __("Subcontrato"), icon: "hard-hat", doctype: "Subcontract" },
			{ label: __("Compra avulsa"), icon: "receipt", doctype: "Work Cost" },
		];
	},

	visible_actions() {
		return this.actions().filter((action) => {
			if (action.route) {
				const dt = action.read_doctype || action.route[1];
				return frappe.perm.has_perm(dt, 0, "read");
			}
			return frappe.model.can_create(action.doctype);
		});
	},

	icon(name) {
		try {
			return frappe.utils.icon(name, "sm") || "";
		} catch (e) {
			return "";
		}
	},

	render(container) {
		const chips = this.visible_actions()
			.map((action) => {
				const route_attr = action.route
					? ` data-route="${frappe.utils.escape_html(action.route.join("/"))}"`
					: "";
				const dt_attr = action.doctype
					? ` data-new-dt="${frappe.utils.escape_html(action.doctype)}"`
					: "";
				return `
			<button type="button" class="eng-dash-action-chip"${dt_attr}${route_attr}>
				${this.icon(action.icon)}
				<span>${frappe.utils.escape_html(action.label)}</span>
			</button>`;
			})
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
			const route = $(this).attr("data-route");
			if (route) {
				frappe.set_route(...route.split("/"));
				return;
			}
			const dt = $(this).attr("data-new-dt");
			if (dt) frappe.new_doc(dt);
		});
	},
};
