frappe.ui.form.on("Project Stage Template", {
	refresh(frm) {
		eng_pst_update_weight_display(frm);
		if ((frm.doc.stages || []).length > 0) {
			frm.add_custom_button(__("Redistribuir Pesos"), function () {
				const n = frm.doc.stages.length;
				const base = Math.floor(10000 / n) / 100;
				const remainder = Math.round((100 - base * n) * 100) / 100;
				frm.doc.stages.forEach((d, idx) => {
					d.weight = idx === n - 1 ? flt(base + remainder, 2) : base;
				});
				frm.refresh_fields();
				eng_pst_update_weight_display(frm);
				frm.dirty();
			});
		}
	},
});

frappe.ui.form.on("Project Stage Template Item", {
	weight(frm) {
		eng_pst_update_weight_display(frm);
	},
	stages_add(frm) {
		eng_pst_update_weight_display(frm);
	},
	stages_remove(frm) {
		eng_pst_update_weight_display(frm);
	},
	stage_type(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.stage_type) {
			frappe.db.get_value(
				"Stage Type",
				row.stage_type,
				["default_weight", "default_order"],
				(r) => {
					if (r) {
						if (flt(r.default_weight) > 0) {
							frappe.model.set_value(cdt, cdn, "weight", r.default_weight);
						}
						if (cint(r.default_order) > 0) {
							frappe.model.set_value(cdt, cdn, "sort_order", r.default_order);
						}
					}
				}
			);
		}
	},
});

function eng_pst_update_weight_display(frm) {
	const total = (frm.doc.stages || []).reduce((sum, d) => sum + (flt(d.weight) || 0), 0);
	const color =
		Math.abs(total - 100) < 0.01 ? "var(--green-600)" : "var(--red-600)";
	if (frm.fields_dict.total_weight_display) {
		frm.fields_dict.total_weight_display.$wrapper.html(
			`<div style="padding:8px 12px;border-radius:6px;background:var(--control-bg);
			  font-size:var(--text-base);display:inline-flex;align-items:center;gap:8px;">
				<span style="color:var(--text-muted)">${__("Soma dos pesos")}:</span>
				<strong style="color:${color};font-size:var(--text-lg)">${total.toFixed(1)}%</strong>
			</div>`
		);
	}
}
