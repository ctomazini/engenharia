frappe.pages["eng-dashboard"] = frappe.pages["eng-dashboard"] || {};

frappe.pages["eng-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Painel de Obras"),
		single_column: true,
	});

	page.$container = $('<div class="eng-dash-root dashboard-root"></div>').appendTo(page.main);
	page.period_days = 7;
	page.eng_dash_list_limits = engenharia.dashboard?.utils?.default_list_limits?.() || {
		timeline: 5,
		payments: 5,
		parcelas: 5,
		despesas: 5,
		comunicacoes: 5,
		deadlines: 5,
		tasks: 5,
	};
	frappe.pages["eng-dashboard"].page = page;

	page.add_button(__("↺ Atualizar"), () => eng_dashboard_load(page));
	eng_dashboard_polish_frappe_chrome();
	eng_dashboard_load(page);
};

frappe.pages["eng-dashboard"].on_page_hide = function () {
	$(document.body).removeClass("engenharia-dash-active");
};

function eng_dashboard_polish_frappe_chrome() {
	$(document.body).addClass("engenharia-dash-active");
}

const ENG_DASH_ASSETS = [
	"/assets/engenharia/css/dashboard.css",
	"/assets/engenharia/js/dashboard/utils.js",
	"/assets/engenharia/js/dashboard/filters.js",
	"/assets/engenharia/js/dashboard/quick_actions.js",
	"/assets/engenharia/js/dashboard/hero.js",
	"/assets/engenharia/js/dashboard/attention.js",
	"/assets/engenharia/js/dashboard/health.js",
	"/assets/engenharia/js/dashboard/kpis.js",
	"/assets/engenharia/js/dashboard/financial.js",
	"/assets/engenharia/js/dashboard/lists.js",
	"/assets/engenharia/js/dashboard/timeline.js",
	"/assets/engenharia/js/dashboard/commissions.js",
	"/assets/engenharia/js/dashboard/operational.js",
];

function eng_dashboard_load(page) {
	if (window.engenharia?.dashboard?.utils?.render_skeleton) {
		engenharia.dashboard.utils.render_skeleton(page.$container);
	} else {
		page.$container.html(`<div class="eng-dash-loading">${__("Carregando painel...")}</div>`);
	}

	frappe.require(ENG_DASH_ASSETS, function () {
		if (!page.eng_dash_list_limits) {
			page.eng_dash_list_limits = engenharia.dashboard.utils.default_list_limits();
		}

		frappe
			.xcall("engenharia.dashboard_api.get_dashboard_data", {
				period_days: page.period_days,
				list_limits: page.eng_dash_list_limits,
			})
			.then((data) => {
				engenharia.dashboard.render_dashboard(page.$container, data, page);
			})
			.catch(() => {
				page.$container.html(
					`<div class="eng-dash-empty-state"><p>${__("Não foi possível carregar o painel.")}</p></div>`
				);
			});
	});
}

frappe.provide("engenharia.dashboard");

engenharia.dashboard.render_dashboard = function ($container, data, page) {
	$container.empty();
	const $content = $('<div class="eng-dash-content dashboard-content"></div>').appendTo($container);

	const $hero = $('<div class="eng-dash-hero-wrap eng-dash-priority-high"></div>').appendTo($content);
	const $filters = $('<div class="eng-dash-filters-wrap"></div>').appendTo($content);
	const $attention = $('<div class="eng-dash-zona-critica"></div>').appendTo($content);
	const $actions = $('<div class="eng-dash-actions-host"></div>').appendTo($content);
	const $agenda = $('<div class="eng-dash-agenda-host"></div>').appendTo($content);
	const $operational = $('<div class="eng-dash-zona-operacional"></div>').appendTo($content);
	const $financeZone = $('<div class="eng-dash-zona-financeira"></div>').appendTo($content);
	const $financeHead = $('<div class="eng-dash-finance-head"></div>').appendTo($financeZone);
	const $health = $('<div></div>').appendTo($financeHead);
	const $kpis = $('<div></div>').appendTo($financeHead);
	const $fin = $('<div></div>').appendTo($financeZone);
	const $lists = $('<div></div>').appendTo($content);

	engenharia.dashboard.hero.render($hero, data);
	engenharia.dashboard.filters.render($filters, data, page);
	engenharia.dashboard.quick_actions.render($actions);
	engenharia.dashboard.attention.render($attention, data);
	engenharia.dashboard.timeline.render($agenda, data, page);
	engenharia.dashboard.operational.render($operational, data);

	if (data.is_manager) {
		engenharia.dashboard.health.render($health, data);
		engenharia.dashboard.kpis.render($kpis, data);
		engenharia.dashboard.financial.render($fin, data, page);
		engenharia.dashboard.lists.render_duo($lists, data, page);
		const $commissions = $('<div class="eng-dash-commissions-host"></div>').appendTo($content);
		engenharia.dashboard.commissions.render($commissions, data);
	} else {
		$financeZone.remove();
	}

	engenharia.dashboard.filters.bind($content, page, eng_dashboard_load);
	engenharia.dashboard.utils.bind_list_limits($content, page, eng_dashboard_load);
	engenharia.dashboard.hero.bind($content);
	engenharia.dashboard.quick_actions.bind($content);
	engenharia.dashboard.attention.bind($content);
};
