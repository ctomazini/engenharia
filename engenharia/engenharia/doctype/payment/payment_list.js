frappe.listview_settings["Payment"] = {
	...(frappe.listview_settings["Payment"] || {}),
	hide_name_column: true,
	add_fields: ["status", "due_date", "amount", "received_amount"],
	get_indicator(doc) {
		const amount = flt(doc.amount);
		const received = flt(doc.received_amount);
		const is_partial =
			received > 0 && amount > 0 && received < amount - 0.009 && doc.status !== "Recebido";

		if (doc.status === "Vencido") {
			return [__("Vencido"), "red", "status,=,Vencido"];
		}
		if (doc.status === "Recebido") {
			return [__("Recebido"), "green", "status,=,Recebido"];
		}
		if (is_partial) {
			return [__("Parcial"), "orange", "status,=," + (doc.status || "Pendente")];
		}
		if (doc.status === "Pendente") {
			return [__("Pendente"), "orange", "status,=,Pendente"];
		}
		if (doc.status === "Cancelado") {
			return [__("Cancelado"), "gray", "status,=,Cancelado"];
		}
		if (doc.status === "Renegociado") {
			return [__("Renegociado"), "blue", "status,=,Renegociado"];
		}
		return [__(doc.status || "Pendente"), "orange", "status,=," + (doc.status || "Pendente")];
	},
};
