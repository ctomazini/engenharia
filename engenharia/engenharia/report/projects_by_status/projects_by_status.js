const STATUS_PILL = {
	"Orçamento": "blue",
	"Em andamento": "green",
	Paralisada: "orange",
	"Concluída": "darkgrey",
	Cancelada: "red",
};

frappe.query_reports["projects_by_status"] = {
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "status" && row.status) {
			const cls = STATUS_PILL[row.status] || "grey";
			return `<span class="indicator-pill ${cls} filterable ellipsis">${row.status}</span>`;
		}
		if (column.fieldname === "count" && row.count) {
			return `<strong>${value}</strong>`;
		}
		return value;
	},
};
