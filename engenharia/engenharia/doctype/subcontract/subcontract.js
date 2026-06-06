frappe.ui.form.on("Subcontract", {
	setup(frm) {
		frm.set_query("project", () => ({
			filters: {
				status: ["not in", ["Cancelada"]],
			},
		}));

		frm.set_query("stage", () => {
			if (!frm.doc.project) {
				return { filters: { name: "" } };
			}
			return {
				filters: {
					project: frm.doc.project,
				},
			};
		});
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

		if (
			!frm.is_new() &&
			frm.doc.status !== "Cancelled" &&
			frappe.user.has_role("Engenharia Manager")
		) {
			frm.add_custom_button(__("Cancelar"), () => {
				frappe.confirm(
					__("Cancelar este subcontrato? Os pagamentos registrados serão mantidos no histórico."),
					() => {
						frappe.model.set_value(frm.doctype, frm.doc.name, "status", "Cancelled").then(() =>
							frm.save()
						);
					}
				);
			});
		}
	},
});
