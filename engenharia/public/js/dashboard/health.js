frappe.provide("engenharia.dashboard");

engenharia.dashboard.health = {
	calc_score(centro, kpis, fin) {
		const vencidos = (centro.parcelas_vencidas && centro.parcelas_vencidas.count) || 0;
		const prazos = (centro.prazos_vencidos || 0) + (centro.prazos_proximos_3d || 0);
		const tarefas = (centro.tarefas_atrasadas || 0) + Math.min(centro.tarefas_pendentes || 0, 5);
		const penalty = vencidos * 12 + prazos * 6 + tarefas * 4;
		const taxa = fin?.taxa_recebimento || kpis?.taxa_recebimento || 0;
		const bonus = Math.min(taxa / 5, 10);
		const score = Math.max(0, Math.min(100, Math.round(100 - penalty + bonus)));
		let tone = "green";
		let label = __("Saudável");
		if (score < 50) {
			tone = "red";
			label = __("Crítico");
		} else if (score < 75) {
			tone = "orange";
			label = __("Atenção");
		}
		return { score, tone, label, vencidos, prazos, tarefas };
	},

	render(container, data) {
		const s = this.calc_score(data.centro_atencao, data.kpis, data.financeiro);
		const circumference = 2 * Math.PI * 36;
		const offset = circumference - (circumference * s.score) / 100;

		container.html(`
			<section class="eng-dash-saude" id="eng-dash-saude">
				<h3>${__("Saúde Operacional")}</h3>
				<div class="eng-dash-saude__body">
					<div class="eng-dash-saude-ring">
						<svg viewBox="0 0 88 88" aria-hidden="true">
							<circle class="eng-dash-saude-ring-bg" cx="44" cy="44" r="36"></circle>
							<circle class="eng-dash-saude-ring-fill tone-${s.tone}" cx="44" cy="44" r="36"
								stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"></circle>
						</svg>
						<div class="eng-dash-saude-score">
							<span class="eng-dash-saude-score__num">${s.score}%</span>
							<span class="eng-dash-saude-score__label">${frappe.utils.escape_html(s.label)}</span>
						</div>
					</div>
					<div>
						<p>${__("Consolidado a partir dos indicadores do painel.")}</p>
						<p><strong>${s.vencidos}</strong> ${__("parcelas vencidas")} ·
						<strong>${s.prazos}</strong> ${__("prazos críticos")} ·
						<strong>${s.tarefas}</strong> ${__("tarefas em risco")}</p>
					</div>
				</div>
			</section>
		`);
	},
};
