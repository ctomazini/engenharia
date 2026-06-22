frappe.listview_settings["Project Stage"] = {
	...(frappe.listview_settings["Project Stage"] || {}),
	hide_name_column: true,
	add_fields: ["status", "progress", "project", "stage_type"],
	get_indicator(doc) {
		const colors = {
			"Não iniciada": "gray",
			"Em andamento": "orange",
			Concluída: "green",
		};
		const status = doc.status || "Não iniciada";
		return [__(status), colors[status] || "gray", "status,=," + status];
	},
};
