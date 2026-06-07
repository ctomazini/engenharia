window.eng_render_placeholder_reference = function (blocks) {
	let html = '<div style="max-height:560px;overflow-y:auto;">';
	html +=
		'<p class="text-muted small" style="margin-bottom:12px;">' +
		__(
			"Sintaxe docxtpl: <code>{{ placeholder }}</code>. Grupos marcados como <em>condicional</em> só têm valor quando há contrato vinculado. A logo usa <code>{{ office_logo }}</code> como imagem inline."
		) +
		"</p>";

	(blocks || []).forEach((block) => {
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
			const loopVar = item.loop_var ? `${item.loop_var}.` : "";
			const loopBadge = item.loop_only
				? ` <span class="indicator-pill blue">${frappe.utils.escape_html(
						`{% for ${item.loop_var || "item"} in ... %}`
				  )}</span>`
				: "";
			html +=
				"<tr><td><code>{{ " +
				frappe.utils.escape_html(loopVar + item.placeholder) +
				" }}</code>" +
				loopBadge +
				"</td>";
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
};
