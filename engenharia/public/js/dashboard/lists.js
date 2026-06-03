frappe.provide("engenharia.dashboard");

engenharia.dashboard.lists = {
	render_duo(container, data) {
		const parcelas = data.parcelas || data.pagamentos || [];
		const despesas = data.despesas_pendentes || [];
		const totalMes = data.total_despesas_mes || 0;
		const utils = engenharia.dashboard.utils;

		const parcelasHtml = parcelas.length
			? parcelas
					.map(
						(p) => `
				<button type="button" class="eng-dash-op-row" data-doctype="Payment" data-name="${frappe.utils.escape_html(p.name)}">
					<div>
						<div class="eng-dash-op-row__title">${frappe.utils.escape_html(p.title || p.name)}</div>
						<div class="eng-dash-op-row__sub">${frappe.utils.escape_html(p.due_date || p.vencimento || "")} · ${frappe.utils.escape_html(p.customer_name || "")}</div>
					</div>
					<div class="eng-dash-op-side">
						${utils.currency_html(p.valor_total != null ? p.valor_total : p.amount, { alignEnd: true })}
						${utils.status_pill(p.status)}
					</div>
				</button>`
					)
					.join("")
			: `<div class="eng-dash-empty">${__("Nenhum recebível no período.")}</div>`;

		const despesasHtml = despesas.length
			? despesas
					.map(
						(d) => `
				<button type="button" class="eng-dash-op-row" data-doctype="Reimbursable Expense" data-name="${frappe.utils.escape_html(d.name)}">
					<div>
						<div class="eng-dash-op-row__title">${frappe.utils.escape_html(d.title || d.name)}</div>
						<div class="eng-dash-op-row__sub">${frappe.utils.escape_html(d.data || d.payment_date || "")} · ${frappe.utils.escape_html(d.customer_name || "")}</div>
					</div>
					<div class="eng-dash-op-side">
						${utils.currency_html(d.valor != null ? d.valor : d.amount, { alignEnd: true })}
						${utils.status_pill(d.status)}
					</div>
				</button>`
					)
					.join("")
			: `<div class="eng-dash-empty">${__("Nenhuma despesa a reembolsar.")}</div>`;

		container.html(`
			<div class="eng-dash-duo">
				<section class="eng-dash-section">
					<h3>${__("A receber")}</h3>
					${parcelasHtml}
				</section>
				<section class="eng-dash-section">
					<h3>${__("A reembolsar")}</h3>
					<p class="eng-dash-section-sub">${__("Mês calendário")}: ${utils.currency_html(totalMes)}</p>
					${despesasHtml}
				</section>
			</div>
		`);

		utils.bind_routes(container);
	},
};
