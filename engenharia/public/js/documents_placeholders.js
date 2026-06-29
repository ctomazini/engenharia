window.eng_render_placeholder_reference = function (blocks) {
	let html = '<div style="max-height:560px;overflow-y:auto;">';
	html +=
		'<p class="text-muted small" style="margin-bottom:12px;">' +
		__(
			"Sintaxe docxtpl: <code>{{ placeholder }}</code>. Grupos <em>condicionais</em> só têm valor quando a condição indicada é atendida. Logotipo: <code>{{ company_logo }}</code> (URL do arquivo em Configurações do Escritório)."
		) +
		"</p>";

	(blocks || []).forEach((block) => {
		let badge = "";
		if (block.condicional) {
			const hint = block.condicional_motivo || __("condicional");
			badge =
				' <span class="indicator-pill orange" title="' +
				frappe.utils.escape_html(hint) +
				'">' +
				__("condicional") +
				"</span>";
		}
		html +=
			'<h5 style="margin-top:14px;margin-bottom:6px;border-bottom:1px solid var(--border-color);padding-bottom:4px;">' +
			frappe.utils.escape_html(block.grupo) +
			badge +
			"</h5>";
		if (block.condicional && block.condicional_motivo) {
			html +=
				'<p class="text-muted small" style="margin:0 0 6px;">' +
				frappe.utils.escape_html(block.condicional_motivo) +
				"</p>";
		}
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

window.eng_render_placeholder_guide = function (sections) {
	const esc = frappe.utils.escape_html;
	let html = '<div style="max-height:560px;overflow-y:auto;">';
	html +=
		'<p class="text-muted small" style="margin-bottom:12px;">' +
		__(
			"Exemplos práticos de uso dos placeholders no modelo .docx. Regra de ouro: use o valor <strong>bruto</strong> para calcular e o filtro <code>| real</code> / <code>| num_br</code> (ou o sufixo <code>_fmt</code>) para exibir em padrão brasileiro."
		) +
		"</p>";

	(sections || []).forEach((section) => {
		html +=
			'<h5 style="margin-top:16px;margin-bottom:4px;border-bottom:1px solid var(--border-color);padding-bottom:4px;">' +
			esc(section.titulo) +
			"</h5>";
		if (section.descricao) {
			html +=
				'<p class="text-muted small" style="margin:0 0 8px;">' +
				esc(section.descricao) +
				"</p>";
		}
		(section.exemplos || []).forEach((ex) => {
			html +=
				'<div style="margin:0 0 10px;padding:8px 10px;border:1px solid var(--border-color);border-radius:6px;background:var(--control-bg);">';
			html +=
				'<div style="font-size:11px;color:var(--text-muted);margin-bottom:2px;">' +
				__("No modelo") +
				"</div>";
			html +=
				'<pre style="margin:0 0 6px;white-space:pre-wrap;font-size:12px;">' +
				esc(ex.codigo) +
				"</pre>";
			if (ex.resultado) {
				html +=
					'<div style="font-size:11px;color:var(--text-muted);margin-bottom:2px;">' +
					__("Resultado") +
					"</div>";
				html +=
					'<pre style="margin:0;white-space:pre-wrap;font-size:12px;color:var(--text-color);">' +
					esc(ex.resultado) +
					"</pre>";
			}
			if (ex.nota) {
				html +=
					'<div class="text-muted small" style="margin-top:6px;">' +
					esc(ex.nota) +
					"</div>";
			}
			html += "</div>";
		});
	});

	html += "</div>";

	frappe.msgprint({
		title: __("Como Usar os Placeholders"),
		message: html,
		wide: true,
		indicator: "green",
	});
};
