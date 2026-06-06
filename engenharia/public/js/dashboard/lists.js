frappe.provide("engenharia.dashboard");

engenharia.dashboard.lists = {
	render_duo(container, data, page) {
		const parcelas = data.parcelas || data.pagamentos || [];
		const despesas = data.despesas_pendentes || [];
		const meta = data.list_meta || {};
		const limits = data.list_limits || page?.eng_dash_list_limits || {};
		const utils = engenharia.dashboard.utils;

		const parcelasHtml = parcelas.length
			? parcelas
					.map((p) => {
						let rowClass = "eng-dash-op-row";
						if (p.status === "Vencido") rowClass += " eng-dash-op-row--overdue";
						else if (p.status === "Pendente") rowClass += " eng-dash-op-row--pending";
						return `
				<div class="eng-dash-op-row-wrap">
					<button type="button" class="${rowClass}" data-doctype="Payment" data-name="${frappe.utils.escape_html(p.name)}">
						<div>
							<div class="eng-dash-op-row__title">${frappe.utils.escape_html(p.title || p.name)}</div>
							<div class="eng-dash-op-row__sub">${frappe.utils.escape_html(p.due_date || p.vencimento || "")} · ${frappe.utils.escape_html(p.customer_name || "")}</div>
						</div>
						<div class="eng-dash-op-side">
							${utils.currency_html(p.valor_total != null ? p.valor_total : p.amount, { alignEnd: true })}
							${utils.status_pill(p.status)}
						</div>
					</button>
					${
						p.status === "Pendente" || p.status === "Vencido"
							? `<button type="button" class="btn btn-xs btn-primary eng-dashboard-btn-receive eng-dash-op-cta" data-mark-payment="${frappe.utils.escape_html(p.name)}">${__("Receber")}</button>`
							: ""
					}
				</div>`;
					})
					.join("")
			: utils.render_empty(__("Nenhum recebível pendente ✓"), "check-circle");

		const despesasHtml = despesas.length
			? despesas
					.map((d) => {
						let rowClass = "eng-dash-op-row";
						if (d.status === "A reembolsar") rowClass += " eng-dash-op-row--pending";
						return `
				<button type="button" class="${rowClass}" data-doctype="Reimbursable Expense" data-name="${frappe.utils.escape_html(d.name)}">
					<div>
						<div class="eng-dash-op-row__title">${frappe.utils.escape_html(d.title || d.name)}</div>
						<div class="eng-dash-op-row__sub">${frappe.utils.escape_html(d.payment_date || "")} · ${frappe.utils.escape_html(d.customer_name || "")}</div>
					</div>
					<div class="eng-dash-op-side">
						${utils.currency_html(d.valor != null ? d.valor : d.amount, { alignEnd: true })}
						${utils.status_pill(d.status)}
					</div>
				</button>`;
					})
					.join("")
			: utils.render_empty(__("Nenhuma despesa a reembolsar ✓"), "check-circle");

		container.html(`
			<div class="eng-dash-duo">
				<section class="eng-dash-section">
					<div class="eng-dash-section-head">
						<div>
							<h3 class="eng-dash-section-title">${__("Parcelas pendentes")}</h3>
							<p class="eng-dash-section-sub">${utils.list_meta_label(meta.parcelas)}</p>
						</div>
						${utils.render_list_limit_controls("parcelas", limits.parcelas || 5, meta.parcelas)}
					</div>
					${parcelasHtml}
					${utils.render_view_all_footer("Payment", meta.parcelas)}
				</section>
				<section class="eng-dash-section">
					<div class="eng-dash-section-head">
						<div>
							<h3 class="eng-dash-section-title">${__("A reembolsar")}</h3>
							<p class="eng-dash-section-sub">${utils.list_meta_label(meta.despesas)}</p>
						</div>
						${utils.render_list_limit_controls("despesas", limits.despesas || 5, meta.despesas)}
					</div>
					${despesasHtml}
					${utils.render_view_all_footer("Reimbursable Expense", meta.despesas)}
				</section>
			</div>
		`);

		utils.bind_routes(container);
		utils.bind_view_all(container);
		this.bind_mark_payment(container);
	},

	bind_mark_payment($root) {
		$root.find(".eng-dash-op-cta[data-mark-payment]").on("click", function (e) {
			e.preventDefault();
			e.stopPropagation();
			const name = $(this).attr("data-mark-payment");
			frappe.call({
				method: "engenharia.dashboard_api.mark_payment_received",
				args: { payment_name: name },
				freeze: true,
				callback() {
					frappe.show_alert({ message: __("Pagamento recebido"), indicator: "green" });
					const page = frappe.pages["eng-dashboard"]?.page;
					if (page) eng_dashboard_load(page);
				},
			});
		});
	},
};
