frappe.provide("engenharia.dashboard");

engenharia.dashboard.next_event = {
	_operational_items(data) {
		return (data.agenda || data.timeline || []).filter((row) => row.type !== "payment");
	},

	render(container, data) {
		const utils = engenharia.dashboard.utils;
		const upcoming = this._operational_items(data).slice(0, 2);

		let bodyHtml;
		if (!upcoming.length) {
			bodyHtml = utils.render_empty(__("Nenhum compromisso pendente ✓"), "check-circle");
		} else {
			const cards = upcoming.map((item) => this._render_compromisso_card(item, utils)).join("");
			bodyHtml = `<div class="eng-dash-centro-grid">${cards}</div>`;
		}

		container.html(`
			<section class="eng-dash-centro" id="eng-dash-proximo-compromisso">
				<div class="eng-dash-section-head">
					<div>
						<h3 class="eng-dash-section-title">${__("Próximos compromissos")}</h3>
						<p class="eng-dash-section-sub">${__("Os dois mais urgentes na agenda")}</p>
					</div>
				</div>
				${bodyHtml}
			</section>
		`);

		utils.bind_routes(container);
	},

	_render_compromisso_card(item, utils) {
		const typeLabel = utils.event_type_label(item.type);
		const time = utils.extract_time_from_sort_key(item.sort_key);
		const tone = item.urgency || "gray";
		const headline = time || item.when_label || "—";
		const metaParts = [item.title || ""];
		if (item.subtitle && item.subtitle !== item.title) {
			metaParts.push(item.subtitle);
		}
		return `
			<button type="button" class="eng-dash-atencao-card eng-dash-compromisso-card tone-${tone}" data-doctype="${frappe.utils.escape_html(item.doctype)}" data-name="${frappe.utils.escape_html(item.docname)}">
				<div class="eng-dash-atencao-icon">${utils.icon(item.icon || "calendar")}</div>
				<div class="eng-dash-atencao-body">
					<div class="eng-dash-atencao-count">${frappe.utils.escape_html(headline)}</div>
					<div class="eng-dash-atencao-label">${frappe.utils.escape_html(typeLabel)}</div>
					<div class="eng-dash-atencao-meta">${frappe.utils.escape_html(metaParts.filter(Boolean).join(" · "))}</div>
				</div>
			</button>`;
	},
};
