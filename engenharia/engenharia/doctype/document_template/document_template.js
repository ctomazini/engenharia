frappe.ui.form.on("Document Template", {
	view_placeholders(frm) {
		frappe.call({
			method: "engenharia.documents.get_placeholder_reference",
			freeze: true,
			freeze_message: __("Carregando placeholders..."),
			callback(r) {
				if (!r.message) {
					return;
				}
				eng_render_placeholder_reference(r.message);
			},
		});
	},
});

function eng_render_placeholder_reference(blocks) {
	let html = '<div style="max-height:560px;overflow-y:auto;">';

	blocks.forEach((block) => {
		const badge = block.condicional
			? ' <span class="indicator-pill orange">condicional</span>'
			: "";
		html +=
			'<h5 style="margin-top:14px;margin-bottom:6px;border-bottom:1px solid var(--border-color);padding-bottom:4px;">' +
			frappe.utils.escape_html(block.grupo) +
			badge +
			"</h5>";
		html +=
			'<table class="table table-condensed table-bordered" style="font-size:12px;">';
		html += "<thead><tr><th>Placeholder</th><th>Label</th><th>Alias legado</th></tr></thead><tbody>";

		(block.items || []).forEach((item) => {
			html +=
				"<tr><td><code>{{ " +
				frappe.utils.escape_html(item.placeholder) +
				" }}</code></td>";
			html += "<td>" + frappe.utils.escape_html(item.label || "") + "</td>";
			html +=
				"<td>" +
				(item.alias
					? "<code>{{ " + frappe.utils.escape_html(item.alias) + " }}</code>"
					: "—") +
				"</td></tr>";
		});
		html += "</tbody></table>";
	});

	html += "</div>";

	frappe.msgprint({
		title: __("Placeholders Disponíveis"),
		message: html,
		wide: true,
		indicator: "blue",
	});
}
