frappe.ui.form.on("Project Document", {
	setup(frm) {
		frm.set_query("related_permit", () => ({
			filters: {
				project: frm.doc.project,
			},
		}));
	},

	project(frm) {
		if (frm.doc.related_permit) {
			frm.set_value("related_permit", "");
		}
	},

	after_save(frm) {
		if (frm.doc.project && typeof eng_hub_refresh_documents_by_project === "function") {
			eng_hub_refresh_documents_by_project(frm.doc.project);
		}
	},
});
