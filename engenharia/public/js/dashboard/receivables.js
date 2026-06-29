frappe.provide("engenharia.dashboard");

engenharia.dashboard.receivables = {
	render($container, data) {
		if (!data.is_manager) return;

		const $wrapper = $(`
			<div class="eng-dash-receivables">
				<button type="button" class="btn btn-sm btn-default eng-dash-btn-receivables">
					<i class="fa fa-file-text-o"></i> ${__("Relatório para Contador")}
				</button>
			</div>
		`);

		$wrapper.find(".eng-dash-btn-receivables").on("click", () => {
			engenharia.dashboard.receivables.show_dialog();
		});

		$container.append($wrapper);
	},

	show_dialog() {
		const now = new Date();
		const month_options = [
			"1 - Janeiro", "2 - Fevereiro", "3 - Março", "4 - Abril",
			"5 - Maio", "6 - Junho", "7 - Julho", "8 - Agosto",
			"9 - Setembro", "10 - Outubro", "11 - Novembro", "12 - Dezembro",
		];

		const d = new frappe.ui.Dialog({
			title: __("Relatório de Recebimentos"),
			fields: [
				{
					fieldname: "mode",
					fieldtype: "Select",
					label: __("Modo"),
					options: [
						{ value: "previsao", label: __("Previsão (vencimentos do mês)") },
						{ value: "realizado", label: __("Realizado (recebidos no mês)") },
					],
					default: "previsao",
					reqd: 1,
				},
				{ fieldtype: "Column Break" },
				{
					fieldname: "month",
					fieldtype: "Select",
					label: __("Mês"),
					options: month_options.join("\n"),
					default: month_options[now.getMonth()],
					reqd: 1,
				},
				{
					fieldname: "year",
					fieldtype: "Int",
					label: __("Ano"),
					default: now.getFullYear(),
					reqd: 1,
				},
				{ fieldtype: "Section Break" },
				{
					fieldname: "template_name",
					fieldtype: "Link",
					label: __("Modelo do Documento"),
					options: "Document Template",
					reqd: 1,
					get_query() {
						return { filters: { enabled: 1 } };
					},
				},
			],
			primary_action_label: __("Gerar Relatório"),
			primary_action(values) {
				const month_num = parseInt(values.month.split(" - ")[0], 10);
				d.hide();
				frappe.show_alert({ message: __("Gerando relatório..."), indicator: "blue" });

				frappe.call({
					method: "engenharia.receivables.get_monthly_receivables_report",
					args: {
						month: month_num,
						year: values.year,
						mode: values.mode,
						template_name: values.template_name,
					},
					callback(r) {
						const msg = r.message;
						if (msg && msg.file_content && msg.count) {
							engenharia.dashboard.receivables._download_docx(
								msg.file_name,
								msg.file_content
							);
							frappe.show_alert({
								message: __("{0} parcela(s) — Total: R$ {1}", [msg.count, msg.total]),
								indicator: "green",
							});
						} else {
							frappe.show_alert({
								message: __("Nenhuma parcela encontrada no período."),
								indicator: "orange",
							});
						}
					},
				});
			},
		});

		d.show();
	},

	_download_docx(file_name, base64_content) {
		const binary = atob(base64_content);
		const bytes = new Uint8Array(binary.length);
		for (let i = 0; i < binary.length; i++) {
			bytes[i] = binary.charCodeAt(i);
		}
		const blob = new Blob([bytes], {
			type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
		});
		const url = URL.createObjectURL(blob);
		const link = document.createElement("a");
		link.href = url;
		link.download = file_name || "Recebimentos.docx";
		link.rel = "noopener";
		link.style.display = "none";
		document.body.appendChild(link);
		link.click();
		window.setTimeout(() => {
			link.remove();
			URL.revokeObjectURL(url);
		}, 1000);
	},
};
