frappe.provide("engenharia.dashboard");

engenharia.dashboard.quick_actions = {
	actions() {
		return [
			{ label: __("Cliente"), icon: "user-plus", doctype: "Customer", tier: "core" },
			{ label: __("Obra"), icon: "folder-plus", doctype: "Construction Project", tier: "core" },
			{ label: __("Prazo"), icon: "clock-plus", doctype: "Deadline", tier: "core" },
			{ label: __("Tarefa"), icon: "list-plus", doctype: "Task", tier: "core" },
			{
				label: __("Calendário"),
				icon: "calendar",
				route: ["List", "Event", "Calendar"],
				read_doctype: "Event",
				tier: "daily",
			},
			{
				label: __("Comunicação"),
				icon: "message-square-plus",
				doctype: "Communication Log",
				tier: "daily",
			},
			{ label: __("Horas"), icon: "clock", doctype: "Time Log", tier: "daily" },
			{ label: __("Recebimento"), icon: "circle-dollar-sign", doctype: "Payment", tier: "finance" },
			{ label: __("Subcontrato"), icon: "hard-hat", doctype: "Subcontract", tier: "finance" },
			{ label: __("Compra avulsa"), icon: "receipt", doctype: "Work Cost", tier: "finance" },
			{ label: __("Despesa escritório"), icon: "building", doctype: "Office Expense", tier: "finance" },
		];
	},

	_is_onboarding(data) {
		const kpis = (data && data.kpis) || {};
		return (kpis.active_projects || 0) === 0;
	},

	visible_actions(data) {
		const permitted = this.actions().filter((action) => {
			if (action.route) {
				const dt = action.read_doctype || action.route[1];
				return frappe.perm.has_perm(dt, 0, "read");
			}
			return frappe.model.can_create(action.doctype);
		});

		if (!this._is_onboarding(data)) {
			return permitted;
		}

		return permitted.filter((action) => action.tier === "core");
	},

	icon(name) {
		try {
			return frappe.utils.icon(name, "sm") || "";
		} catch (e) {
			return "";
		}
	},

	render(container, data) {
		const onboarding = this._is_onboarding(data);
		const chips = this.visible_actions(data)
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

		const label = onboarding ? __("Primeiros passos") : __("Ações rápidas");
		const hint = onboarding
			? `<p class="eng-dash-actions-hint">${__(
					"Comece cadastrando um cliente e abrindo a primeira obra."
			  )}</p>`
			: "";

		container.html(`
			<div class="eng-dash-actions-wrap">
				<p class="eng-dash-actions-label">${label}</p>
				${hint}
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
