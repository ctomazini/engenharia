frappe.provide("engenharia.dashboard");

engenharia.dashboard.hero = {
	render(container, data) {
		const resumo = data.resumo || {};
		const period = data.periodo_dias || data.period_days || 7;
		const utils = engenharia.dashboard.utils;
		const greeting = utils.greeting_for_hour();
		const isHigh = resumo.urgency === "high";
		const urgencyLabel = isHigh ? __("Atenção hoje") : __("Operação estável");
		const urgencyClass = isHigh ? "eng-dash-urgency-badge--high" : "eng-dash-urgency-badge--normal";
		const context = period === 1 ? __("Visão de hoje") : __("Visão dos próximos {0} dias", [period]);
		const next = (data.agenda || data.timeline || [])[0];
		const nextEventHtml = next ? this._render_next_event(next, utils) : this._render_next_empty(utils);

		container.html(`
			<header class="eng-dash-hero">
				<div class="eng-dash-hero__top">
					<div>
						<h2 class="eng-dash-hero__greeting">${frappe.utils.escape_html(greeting)}</h2>
						<p class="eng-dash-hero__date">${frappe.utils.escape_html(resumo.date_label || "")}</p>
					</div>
					<span class="eng-dash-urgency-badge ${urgencyClass}">${frappe.utils.escape_html(urgencyLabel)}</span>
				</div>
				<p class="eng-dash-hero__context">${frappe.utils.escape_html(context)}</p>
			</header>
			${nextEventHtml}
		`);
	},

	_render_next_event(item, utils) {
		const typeLabel = utils.event_type_label(item.type);
		const time = utils.extract_time_from_sort_key(item.sort_key);
		const tone = item.urgency || "gray";
		return `
			<button type="button" class="eng-dash-next-event tone-${tone} eng-dash-next-event--type-${frappe.utils.escape_html(item.type || "default")}" data-doctype="${frappe.utils.escape_html(item.doctype)}" data-name="${frappe.utils.escape_html(item.docname)}">
				<div class="eng-dash-next-event__badge">${__("Próximo compromisso")}</div>
				<div class="eng-dash-next-event__body">
					<div class="eng-dash-next-event__icon">${utils.icon(item.icon || "calendar", "md")}</div>
					<div class="eng-dash-next-event__content">
						<div class="eng-dash-next-event__type">
							${frappe.utils.escape_html(typeLabel)}
							<span class="eng-dash-next-event__when tone-${tone}">${frappe.utils.escape_html(item.when_label || "")}${time ? ` · ${frappe.utils.escape_html(time)}` : ""}</span>
						</div>
						<div class="eng-dash-next-event__title">${frappe.utils.escape_html(item.title || "")}</div>
						${item.subtitle ? `<div class="eng-dash-next-event__sub">${frappe.utils.escape_html(item.subtitle)}</div>` : ""}
					</div>
					${item.amount ? `<div class="eng-dash-next-event__amount">${utils.currency_html(item.amount, { alignEnd: true })}</div>` : ""}
				</div>
			</button>`;
	},

	_render_next_empty(utils) {
		return `
			<div class="eng-dash-next-event eng-dash-next-event--empty">
				<div class="eng-dash-next-event__icon">${utils.icon("calendar-check", "md")}</div>
				<div class="eng-dash-next-event__content">
					<div class="eng-dash-next-event__title">${__("Nenhum compromisso pendente ✓")}</div>
				</div>
			</div>`;
	},

	bind($root) {
		engenharia.dashboard.utils.bind_routes($root);
	},
};
