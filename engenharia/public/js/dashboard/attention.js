frappe.provide("engenharia.dashboard");

engenharia.dashboard.attention = {
	render(container, data) {
		const atencao = data.atencao || {};
		const period = data.periodo_dias || data.period_days || 7;
		const utils = engenharia.dashboard.utils;
		const urgent = atencao.urgent || [];
		const periodTiles = atencao.period || [];
		const allTiles = atencao.tiles || urgent.concat(periodTiles);

		container.data("atencao-tiles", allTiles);

		const renderGroup = (title, tiles, offset = 0) => {
			if (!tiles.length) return "";
			const cards = tiles
				.map((tile, idx) => {
					const index = offset + idx;
					const meta = tile.meta_currency != null ? utils.currency_html(tile.meta_currency) : tile.meta ? frappe.utils.escape_html(String(tile.meta)) : "";
					const pulse = tile.pulse ? " eng-dash-atencao-card--pulse" : "";
					const zero = tile.count === 0 ? " eng-dash-atencao-card--ok" : "";
					return `
					<button type="button" class="eng-dash-atencao-card tone-${tile.tone}${pulse}${zero}" data-atencao-index="${index}">
						<div class="eng-dash-atencao-icon">${utils.icon(tile.icon || "alert-circle")}</div>
						<div class="eng-dash-atencao-body">
							<div class="eng-dash-atencao-count">${frappe.utils.escape_html(String(tile.count))}</div>
							<div class="eng-dash-atencao-label">${frappe.utils.escape_html(tile.label || "")}</div>
							${meta ? `<div class="eng-dash-atencao-meta">${meta}</div>` : ""}
						</div>
					</button>`;
				})
				.join("");
			return `
				<div class="eng-dash-centro-group">
					<h4 class="eng-dash-centro-group-title">${frappe.utils.escape_html(title)}</h4>
					<div class="eng-dash-centro-grid">${cards}</div>
				</div>`;
		};

		container.html(`
			<section class="eng-dash-centro eng-dash-priority-max" id="eng-dash-centro-atencao">
				<div class="eng-dash-section-head">
					<div>
						<h3 class="eng-dash-section-title">${__("Zona de Atenção")}</h3>
						<p class="eng-dash-section-sub">${__("O que exige ação agora — próximos {0} dias", [period])}</p>
					</div>
				</div>
				<div class="eng-dash-centro-groups">
					${renderGroup(__("Urgente"), urgent, 0)}
					${renderGroup(__("No período"), periodTiles, urgent.length)}
				</div>
			</section>
		`);
	},

	bind($root) {
		engenharia.dashboard.utils.bind_attention_routes($root);
	},
};
