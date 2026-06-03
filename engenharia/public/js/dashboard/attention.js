frappe.provide("engenharia.dashboard");

engenharia.dashboard.attention = {
	render(container, data) {
		const centro = data.centro_atencao || {};
		const period = data.periodo_dias || data.period_days || 7;
		const tiles = [
			{
				tone: "red",
				count: (centro.parcelas_vencidas && centro.parcelas_vencidas.count) || 0,
				label: __("Parcelas vencidas"),
				meta: centro.parcelas_vencidas?.valor,
				is_money: true,
			},
			{
				tone: "orange",
				count: (centro.pagamentos_periodo && centro.pagamentos_periodo.count) || 0,
				label: period === 1 ? __("A receber hoje") : __("A receber no período"),
				meta: centro.pagamentos_periodo?.valor,
				is_money: true,
			},
			{
				tone: "green",
				count: (centro.recebimentos_periodo && centro.recebimentos_periodo.count) || 0,
				label: __("Recebidos no período"),
				meta: centro.recebimentos_periodo?.valor,
				is_money: true,
			},
			{
				tone: "blue",
				count: centro.prazos_proximos_3d || 0,
				label: __("Prazos em 3 dias"),
			},
			{
				tone: "red",
				count: centro.prazos_vencidos || 0,
				label: __("Prazos vencidos"),
			},
			{
				tone: "orange",
				count: centro.tarefas_atrasadas || 0,
				label: __("Tarefas atrasadas"),
			},
		];

		const html = tiles
			.map((tile) => {
				const meta = tile.is_money
					? engenharia.dashboard.utils.currency_html(tile.meta || 0)
					: tile.meta
						? frappe.utils.escape_html(String(tile.meta))
						: "";
				return `
				<button type="button" class="eng-dash-tile tone-${tile.tone}">
					<div class="eng-dash-tile__count">${frappe.utils.escape_html(String(tile.count))}</div>
					<div class="eng-dash-tile__label">${frappe.utils.escape_html(tile.label)}</div>
					${meta ? `<div class="eng-dash-tile__meta">${meta}</div>` : ""}
				</button>`;
			})
			.join("");

		container.html(`
			<section class="eng-dash-centro">
				<h3>${__("Centro de Atenção")}</h3>
				<div class="eng-dash-centro__grid">${html}</div>
			</section>
		`);
	},
};
