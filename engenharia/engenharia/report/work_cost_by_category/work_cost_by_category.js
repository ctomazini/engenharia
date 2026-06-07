frappe.query_reports["work_cost_by_category"] = {
	filters: [
		{
			fieldname: "cost_category",
			label: __("Categoria de Custo"),
			fieldtype: "Link",
			options: "Cost Category",
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "total_cost") {
			return `<span class="text-danger bold">${value}</span>`;
		}
		if (column.fieldname === "share_percent" && flt(row.share_percent) >= 20) {
			return `<span class="text-warning bold">${value}</span>`;
		}
		return value;
	},
};
