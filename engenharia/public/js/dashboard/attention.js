frappe.provide("engenharia.dashboard");

engenharia.dashboard.attention = {
	render(container, data) {
		const atencao = data.atencao || {};
		const utils = engenharia.dashboard.utils;
		const tiles = (atencao.tiles || []).filter((tile) => cint(tile.count) > 0);

		container.data("atencao-tiles", tiles);

		let bodyHtml;
		if (atencao.all_clear || !tiles.length) {
			bodyHtml = utils.render_empty(atencao.empty_label || __("Nada exige ação agora"), "check-circle");
		} else {
			const cards = tiles
				.map((tile, index) => {
					const meta =
						tile.meta != null
							? frappe.utils.escape_html(String(tile.meta))
							: tile.meta_currency != null
								? utils.currency_html(tile.meta_currency)
								: "";
					const pulse = tile.pulse ? " eng-dash-atencao-card--pulse" : "";
					return `
					<button type="button" class="eng-dash-atencao-card tone-${tile.tone}${pulse}" data-atencao-index="${index}">
						<div class="eng-dash-atencao-icon">${utils.icon(tile.icon || "alert-circle")}</div>
						<div class="eng-dash-atencao-body eng-dashboard-atencao-body">
							<div class="eng-dash-atencao-count">${frappe.utils.escape_html(String(tile.count))}</div>
							<div class="eng-dash-atencao-label">${frappe.utils.escape_html(tile.label || "")}</div>
							${meta ? `<div class="eng-dash-atencao-meta">${meta}</div>` : ""}
						</div>
					</button>`;
				})
				.join("");
			bodyHtml = `
				<div class="eng-dash-centro-grid">${cards}</div>
				<p class="eng-dash-atencao-ok">${frappe.utils.escape_html(atencao.ok_summary || __("Resto em dia ✓"))}</p>`;
		}

		container.html(`
			<section class="eng-dash-centro" id="eng-dash-centro-atencao">
				<div class="eng-dash-section-head">
					<div>
						<h3 class="eng-dash-section-title">${__("Zona de Atenção")}</h3>
						<p class="eng-dash-section-sub eng-dash-atencao-subtitle">${__("Somente o que exige ação agora")}</p>
					</div>
				</div>
				${bodyHtml}
			</section>
		`);
	},

	bind($root) {
		engenharia.dashboard.utils.bind_attention_routes($root);
	},
};
