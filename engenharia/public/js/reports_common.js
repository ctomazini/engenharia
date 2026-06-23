frappe.provide("engenharia.reports");

/** Mantém layout fixo do Frappe (scroll horizontal) — fluid quebra colunas em tabelas largas. */
engenharia.reports.get_datatable_options = function (options) {
	options.layout = options.layout || "fixed";
	return options;
};

engenharia.reports.SOURCE_BADGE = {
	[__("Compra avulsa")]: "blue",
	[__("Custo Direto")]: "blue",
	[__("Despesa Reembolsável")]: "orange",
	[__("Subcontrato")]: "green",
};

engenharia.reports.STATUS_BADGE = {
	Pago: "green",
	Paid: "green",
	Recebido: "green",
	Reembolsado: "green",
	Open: "blue",
	"Em aberto": "blue",
	Pendente: "orange",
	Pending: "orange",
	"A reembolsar": "orange",
	"Partially Paid": "purple",
	"Parcialmente reembolsado": "purple",
	"Parcialmente paga": "purple",
	Vencido: "red",
	Vencida: "red",
	Cancelado: "gray",
	Cancelled: "gray",
	Cancelada: "gray",
	Orçamento: "blue",
	"Em andamento": "green",
	Paralisada: "orange",
	"Concluída": "gray",
};

engenharia.reports.badge = function (text, color) {
	if (!text) return "";
	return `<span class="eng-hub-badge eng-hub-badge--${color || "gray"}">${frappe.utils.escape_html(
		text
	)}</span>`;
};

engenharia.reports.link = function (route, label) {
	if (!route) return label || "";
	const parts = route.split("/");
	const href =
		parts.length >= 3
			? `/app/${frappe.router.slug(parts[1])}/${encodeURIComponent(parts[2])}`
			: "#";
	return `<a href="${href}">${frappe.utils.escape_html(label || parts[2] || "")}</a>`;
};

engenharia.reports.withCommonFormatter = function (customFormatter) {
	const wrapped = function (value, row, column, data, default_formatter) {
		let formatted = default_formatter(value, row, column, data);
		const fieldname = column.fieldname || column.id;

		if (fieldname === "source_label" && row.source_label) {
			const color = engenharia.reports.SOURCE_BADGE[row.source_label] || "gray";
			formatted = engenharia.reports.badge(row.source_label, color);
		} else if (fieldname === "status" && row.status) {
			const color = engenharia.reports.STATUS_BADGE[row.status] || "gray";
			formatted = engenharia.reports.badge(row.status, color);
		} else if (fieldname === "type" && row.type) {
			const color = row.type === __("Entrada") ? "green" : "red";
			formatted = engenharia.reports.badge(row.type, color);
		} else if (fieldname === "budget_variance" && row.budget_total) {
			const color = flt(row.budget_variance) >= 0 ? "green-600" : "red-600";
			formatted = `<span class="eng-rpt-num" style="color:var(--${color})">${formatted}</span>`;
		} else if (fieldname === "budget_used_percent" && row.budget_total) {
			const pct = flt(row.budget_used_percent);
			let color = "green-600";
			if (pct > 100) color = "red-600";
			else if (pct > 85) color = "orange-500";
			formatted = `<span class="eng-rpt-num" style="color:var(--${color})">${formatted}</span>`;
		} else if (fieldname === "realized_margin" || fieldname === "contractual_margin") {
			const num = flt(row[fieldname]);
			const color = num >= 0 ? "green-600" : "red-600";
			formatted = `<span class="eng-rpt-num" style="color:var(--${color})">${formatted}</span>`;
		} else if (fieldname === "project_title" && row.project) {
			formatted = engenharia.reports.link(
				`Form/Construction Project/${row.project}`,
				row.project_title || row.project
			);
		} else if (fieldname === "source_doc" && row.source_doc && row.source_doctype) {
			formatted = engenharia.reports.link(
				`Form/${row.source_doctype}/${row.source_doc}`,
				row.source_doc
			);
		} else if (fieldname === "description" && row.description) {
			const esc = frappe.utils.escape_html(row.description);
			formatted = `<span class="eng-rpt-desc" title="${esc}">${esc}</span>`;
		} else if (
			[
				"amount",
				"paid",
				"outstanding",
				"total_cost",
				"budget_total",
				"realized_committed",
				"realized_paid",
				"contract_value",
				"received_revenue",
				"reimbursable_expense",
				"inflow",
				"outflow",
				"balance",
			].includes(fieldname)
		) {
			formatted = `<span class="eng-rpt-num">${formatted}</span>`;
		}

		if (customFormatter) {
			formatted = customFormatter(value, row, column, data, () => formatted);
		}

		return formatted;
	};
	wrapped._eng_common_wrapped = true;
	return wrapped;
};

engenharia.reports.enhanceReportSettings = function (reportName) {
	const settings = frappe.query_reports[reportName];
	if (!settings || settings._eng_visual_enhanced) {
		return;
	}

	const existingFormatter = settings.formatter;
	if (existingFormatter?._eng_common_wrapped) {
		settings._eng_visual_enhanced = true;
		return;
	}
	settings.formatter = engenharia.reports.withCommonFormatter(
		existingFormatter
			? function (value, row, column, data, default_formatter) {
					return existingFormatter(value, row, column, data, default_formatter);
				}
			: null
	);

	if (!settings.get_chart_data) {
		settings.get_chart_data = function (chart) {
			return chart;
		};
	}

	settings._eng_visual_enhanced = true;
};

engenharia.reports.applyReportPage = function (report) {
	report.page?.main?.addClass?.("eng-report-page");
};
