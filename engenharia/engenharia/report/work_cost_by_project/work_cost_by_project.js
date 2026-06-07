frappe.query_reports["work_cost_by_project"] = {
	filters: [
		{
			fieldname: "project",
			label: __("Obra"),
			fieldtype: "Link",
			options: "Construction Project",
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "total_cost") {
			return `<span class="text-danger bold">${value}</span>`;
		}
		if (column.fieldname === "share_percent" && flt(row.share_percent) >= 15) {
			return `<span class="text-warning bold">${value}</span>`;
		}
		return value;
	},
};
