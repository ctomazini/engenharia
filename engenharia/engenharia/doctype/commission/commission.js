frappe.ui.form.on("Commission", {
	setup(frm) {
		frm.set_query("construction_project", () => ({
			filters: {
				status: ["not in", ["Cancelada"]],
			},
		}));
	},

	refresh(frm) {
		frm.set_indicator_formatter("status", (doc) => {
			const map = {
				Open: "orange",
				"Partially Paid": "blue",
				Paid: "green",
				Cancelled: "red",
			};
			return map[doc.status] || "gray";
		});
	},
});
