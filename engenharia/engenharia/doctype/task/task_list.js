frappe.listview_settings["Task"] = {
	...(frappe.listview_settings["Task"] || {}),
	hide_name_column: true,
	add_fields: ["status", "priority", "due_date", "project"],
	get_indicator(doc) {
		const colors = {
			"A fazer": "gray",
			Fazendo: "orange",
			Feito: "green",
			Cancelada: "red",
		};
		const status = doc.status || "A fazer";
		return [__(status), colors[status] || "gray", "status,=," + status];
	},
	onload(listview) {
		if (!listview.filter_area.filter_list.get_filter("project")) {
			return;
		}
	},
};
