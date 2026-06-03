frappe.pages["eng-dashboard"] = frappe.pages["eng-dashboard"] || {};

frappe.pages["eng-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Painel de Obras"),
		single_column: true,
	});

	page.$container = $('<div class="eng-dash-root"></div>').appendTo(page.main);
	page.period_days = 7;
	frappe.pages["eng-dashboard"].page = page;

	page.add_button(__("↺ Atualizar"), () => eng_dashboard_load(page));
	eng_dashboard_load(page);
};

const ENG_DASH_ASSETS = [
	"/assets/engenharia/css/dashboard.css",
	"/assets/engenharia/js/dashboard/utils.js",
	"/assets/engenharia/js/dashboard/hero.js",
	"/assets/engenharia/js/dashboard/attention.js",
	"/assets/engenharia/js/dashboard/health.js",
	"/assets/engenharia/js/dashboard/kpis.js",
	"/assets/engenharia/js/dashboard/financial.js",
	"/assets/engenharia/js/dashboard/lists.js",
	"/assets/engenharia/js/dashboard/timeline.js",
];

function eng_dashboard_load(page) {
	page.$container.html(`<div class="eng-dash-loading">${__("Carregando painel...")}</div>`);

	frappe.require(ENG_DASH_ASSETS, function () {
		frappe
			.xcall("engenharia.dashboard_api.get_dashboard_data", {
				period_days: page.period_days,
			})
			.then((data) => {
				engenharia.dashboard.render_dashboard(page.$container, data, page);
			});
	});
}

frappe.provide("engenharia.dashboard");

engenharia.dashboard.render_dashboard = function ($container, data, page) {
	$container.empty();
	const $content = $('<div class="eng-dash-content"></div>').appendTo($container);

	const $hero = $('<div class="eng-dash-hero-wrap"></div>').appendTo($content);
	const $zona = $('<div class="eng-dash-zona-critica"></div>').appendTo($content);
	const $centro = $('<div></div>').appendTo($zona);
	const $destaques = $('<div class="eng-dash-destaques-grid"></div>').appendTo($zona);
	const $saude = $('<div></div>').appendTo($destaques);
	const $kpis = $('<div></div>').appendTo($content);
	const $timeline = $('<div></div>').appendTo($content);
	const $fin = $('<div></div>').appendTo($content);
	const $lists = $('<div></div>').appendTo($content);

	engenharia.dashboard.hero.render($hero, data);
	engenharia.dashboard.attention.render($centro, data);
	engenharia.dashboard.health.render($saude, data);
	engenharia.dashboard.kpis.render($kpis, data);
	engenharia.dashboard.timeline.render($timeline, data);
	engenharia.dashboard.financial.render($fin, data, page);
	engenharia.dashboard.lists.render_duo($lists, data);
};
