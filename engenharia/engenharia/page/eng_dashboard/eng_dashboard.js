frappe.pages["eng-dashboard"] = frappe.pages["eng-dashboard"] || {};

frappe.pages["eng-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Painel de Obras"),
		single_column: true,
	});

	page.$container = $('<div class="eng-dash-root"></div>').appendTo(page.main);
	eng_dashboard_inject_styles();

	page.add_button(__("↺ Atualizar"), () => eng_dashboard_load(page));

	page.period_days = 7;
	frappe.pages["eng-dashboard"].page = page;
	eng_dashboard_load(page);
};

function eng_dashboard_inject_styles() {
	$("#eng-dashboard-styles").remove();
	$("head").append(`
		<style id="eng-dashboard-styles">
			.eng-dash-root { max-width: 1200px; margin: 0 auto; padding: 8px 0 48px; }
			.eng-dash-hero { margin-bottom: 24px; }
			.eng-dash-hero h2 { margin: 0 0 6px; font-weight: 600; }
			.eng-dash-hero p { margin: 0; color: var(--text-muted); }
			.eng-dash-kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 24px; }
			.eng-dash-kpi { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; box-shadow: var(--shadow-sm); }
			.eng-dash-kpi__label { font-size: 12px; color: var(--text-muted); margin-bottom: 8px; }
			.eng-dash-kpi__value { font-size: 22px; font-weight: 700; font-variant-numeric: tabular-nums; }
			.eng-dash-kpi__sub { font-size: 12px; color: var(--text-muted); margin-top: 6px; }
			.eng-dash-section { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; margin-bottom: 16px; }
			.eng-dash-section h3 { margin: 0 0 12px; font-size: 14px; text-transform: uppercase; letter-spacing: .04em; color: var(--text-muted); }
			.eng-dash-chart-row { display: grid; grid-template-columns: 120px 1fr 110px; gap: 10px; align-items: center; margin-bottom: 10px; }
			.eng-dash-chart-track { height: 8px; background: color-mix(in srgb, var(--border-color) 60%, transparent); border-radius: 999px; overflow: hidden; }
			.eng-dash-chart-bar { height: 100%; border-radius: 999px; }
			.eng-dash-chart-bar--warning { background: var(--orange-500); }
			.eng-dash-chart-bar--danger { background: var(--red-500); }
			.eng-dash-chart-bar--neutral { background: var(--gray-500); }
			.eng-dash-chart-bar--info { background: var(--blue-500); }
			.eng-dash-list, .eng-dash-timeline, .eng-dash-alerts { display: grid; gap: 8px; }
			.eng-dash-list-item, .eng-dash-timeline-item, .eng-dash-alert { text-align: left; border: 1px solid var(--border-color); background: var(--control-bg); border-radius: 10px; padding: 10px 12px; cursor: pointer; }
			.eng-dash-list-item:hover, .eng-dash-timeline-item:hover, .eng-dash-alert:hover { border-color: var(--primary); }
			.eng-dash-list-item__title, .eng-dash-timeline-item__title { font-weight: 600; }
			.eng-dash-list-item__meta, .eng-dash-timeline-item__meta { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
			.eng-dash-empty { color: var(--text-muted); font-size: 13px; padding: 8px 0; }
			.eng-dash-hours { display: flex; gap: 24px; font-size: 13px; color: var(--text-muted); }
			.eng-dash-loading { padding: 48px; text-align: center; color: var(--text-muted); }
		</style>
	`);
}

function eng_dashboard_load(page) {
	page.$container.html(`<div class="eng-dash-loading">${__("Carregando painel...")}</div>`);

	frappe.require(
		[
			"/assets/engenharia/js/dashboard/utils.js",
			"/assets/engenharia/js/dashboard/kpis.js",
			"/assets/engenharia/js/dashboard/financial.js",
			"/assets/engenharia/js/dashboard/timeline.js",
		],
		function () {
			frappe.xcall("engenharia.dashboard_api.get_dashboard_data", {
				period_days: page.period_days,
			}).then((data) => {
				page.$container.empty();
				const hero = $(`
					<div class="eng-dash-hero">
						<h2>${frappe.utils.escape_html((data.resumo && data.resumo.date_label) || __("Painel"))}</h2>
						<p>${__("Período")}: ${data.period_days} ${__("dias")}</p>
					</div>
				`);
				const kpiWrap = $('<div class="eng-dash-kpi-wrap"></div>');
				const finWrap = $('<div class="eng-dash-fin-wrap"></div>');
				const timeWrap = $('<div class="eng-dash-time-wrap"></div>');

				page.$container.append(hero, kpiWrap, finWrap, timeWrap);
				engenharia.dashboard.kpis.render(kpiWrap, data);
				engenharia.dashboard.financial.render(finWrap, data);
				engenharia.dashboard.timeline.render(timeWrap, data);
			});
		}
	);
}
