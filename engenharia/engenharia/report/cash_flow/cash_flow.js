frappe.query_reports["cash_flow"] = {
	filters: [
		{
			fieldname: "months",
			label: __("Horizonte (meses)"),
			fieldtype: "Select",
			options: "3\n6\n12",
			default: "6",
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "type" && row.type) {
			const cls = row.type === __("Entrada") ? "green" : "red";
			return `<span class="indicator-pill ${cls} filterable ellipsis">${row.type}</span>`;
		}
		if (column.fieldname === "description" && row.description && !row.date) {
			return `<strong>${row.description}</strong>`;
		}
		return value;
	},
};
