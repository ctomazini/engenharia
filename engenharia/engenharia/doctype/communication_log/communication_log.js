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
