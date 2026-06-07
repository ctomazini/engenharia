frappe.query_reports["project_margin"] = {
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
		if (!row.project) {
			return value;
		}
		if (column.fieldname === "realized_margin" || column.fieldname === "contractual_margin") {
			const amount = flt(row[column.fieldname]);
			if (amount < 0) {
				return `<span class="text-danger bold">${value}</span>`;
			}
			if (amount > 0) {
				return `<span class="text-success bold">${value}</span>`;
			}
		}
		if (column.fieldname === "received_percent") {
			const pct = flt(row.received_percent);
			let cls = "text-warning";
			if (pct >= 100) {
				cls = "text-success";
			} else if (pct >= 50) {
				cls = "text-primary";
			}
			return `<span class="${cls} bold">${value}</span>`;
		}
		return value;
	},
};
