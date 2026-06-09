frappe.query_reports["consolidated_cost"] = {
	filters: [
		{
			fieldname: "project",
			label: __("Obra"),
			fieldtype: "Link",
			options: "Construction Project",
			reqd: 1,
		},
		{
			fieldname: "from_date",
			label: __("De"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("Até"),
			fieldtype: "Date",
		},
		{
			fieldname: "cost_type",
			label: __("Tipo de custo"),
			fieldtype: "Select",
			options: "\nwork_cost\nreimbursable_expense\nsubcontract",
		},
		{
			fieldname: "category",
			label: __("Categoria"),
			fieldtype: "Link",
			options: "Cost Category",
		},
		{
			fieldname: "supplier",
			label: __("Fornecedor"),
			fieldtype: "Link",
			options: "Supplier",
		},
		{
			fieldname: "stage",
			label: __("Etapa"),
			fieldtype: "Link",
			options: "Project Stage",
		},
		{
			fieldname: "funded_by",
			label: __("Quem arca"),
			fieldtype: "Select",
			options: "\nEscritório\nCliente",
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "source_label" && row.source_label) {
			const map = {
				[__("Custo Direto")]: "blue",
				[__("Despesa Reembolsável")]: "orange",
				[__("Subcontrato")]: "green",
			};
			const cls = map[row.source_label] || "gray";
			return `<span class="indicator-pill ${cls} filterable ellipsis">${row.source_label}</span>`;
		}
		if (column.fieldname === "status" && row.status) {
			const paid = ["Pago", "Reembolsado", "Paid", "Closed"];
			const cancelled = ["Cancelado", "Cancelled"];
			let cls = "orange";
			if (paid.includes(row.status)) cls = "green";
			else if (cancelled.includes(row.status)) cls = "gray";
			else if (row.status === "Open") cls = "blue";
			return `<span class="indicator-pill ${cls} filterable ellipsis">${row.status}</span>`;
		}
		if (column.fieldname === "source_doc" && row.source_doc && row.source_doctype) {
			return `<a href="/app/${frappe.router.slug(row.source_doctype)}/${encodeURIComponent(
				row.source_doc
			)}">${row.source_doc}</a>`;
		}
		return value;
	},
	get_chart_data(chart) {
		return chart;
	},
};
