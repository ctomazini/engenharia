frappe.query_reports["projects_by_status"] = {
	formatter(value, row, column, data, default_formatter) {
		if (column.fieldname === "count" && row.count) {
			return `<strong>${default_formatter()}</strong>`;
		}
		return default_formatter();
	},
};
