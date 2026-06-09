var COMMUNICATION_TYPE_COLORS = {
	Telefone: "blue",
	WhatsApp: "green",
	Email: "orange",
	"Reunião Presencial": "purple",
	"Reunião Virtual": "cyan",
	Outro: "grey",
};

frappe.ui.form.on("Communication Log", {
	refresh: function (frm) {
		var color = COMMUNICATION_TYPE_COLORS[frm.doc.communication_type] || "grey";
		if (frm.doc.communication_type) {
			frm.page.set_indicator(frm.doc.communication_type, color);
		}

		if (frm.doc.project && !frm.is_new()) {
			frm.add_custom_button(__("Ver Obra"), function () {
				frappe.set_route("Form", "Construction Project", frm.doc.project);
			});
		}
	},
	create_task(frm) {
		if (frm.doc.create_task && !frm.doc.follow_up_date) {
			frm.set_value(
				"follow_up_date",
				frappe.datetime.add_days(frappe.datetime.nowdate(), 3)
			);
		}
	},
});
