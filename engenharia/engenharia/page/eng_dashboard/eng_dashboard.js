frappe.pages["eng-dashboard"] = frappe.pages["eng-dashboard"] || {};

frappe.pages["eng-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Painel de Obras"),
		single_column: true,
	});

	page.$container = $('<div class="eng-dash-root eng-dashboard-container dashboard-root"></div>').appendTo(page.main);
	page.period_days = 7;
	page.eng_dash_list_limits = engenharia.dashboard?.utils?.default_list_limits?.() || {
		timeline: 5,
		payments: 5,
		parcelas: 5,
		despesas: 5,
		comunicacoes: 5,
		deadlines: 5,
		tasks: 5,
		operational: 5,
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
	"/assets/engenharia/js/dashboard/next_event.js",
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

function eng_dashboard_fetch_data(page) {
	if (!page.eng_dash_list_limits) {
		page.eng_dash_list_limits = engenharia.dashboard?.utils?.default_list_limits?.() || {};
	}
	return frappe.xcall("engenharia.dashboard_api.get_dashboard_data", {
		period_days: page.period_days,
		list_limits: page.eng_dash_list_limits,
	});
}

function eng_dashboard_bind_list_limits_once(page) {
	if (page.eng_dash_list_limits_bound || !engenharia.dashboard?.utils?.bind_list_limits) {
		return;
	}
	page.eng_dash_list_limits_bound = true;
	engenharia.dashboard.utils.bind_list_limits(
		page.$container,
		page,
		eng_dashboard_refresh_list_sections
	);
}

function eng_dashboard_bind_period_filters_once(page) {
	if (page.eng_dash_period_filters_bound || !engenharia.dashboard?.filters?.bind) {
		return;
	}
	page.eng_dash_period_filters_bound = true;
	engenharia.dashboard.filters.bind(
		page.$container,
		page,
		eng_dashboard_refresh_period_sections
	);
}

function eng_dashboard_refresh_period_sections(page) {
	const $container = page.$container;
	if (!$container.find(".eng-dash-content").length) {
		eng_dashboard_load(page);
		return;
	}

	const utils = engenharia.dashboard.utils;
	const scroll = utils.save_scroll($container);
	engenharia.dashboard.filters.update_ui($container, page.period_days);

	eng_dashboard_fetch_data(page)
		.then((data) => {
			page.eng_dash_data = data;

			const patch = (selector, fn) => {
				const $host = $container.find(selector).first();
				if (!$host.length) {
					return false;
				}
				return utils.patch_host($host, () => fn($host, data, page));
			};

			let ok = true;
			ok = patch(".eng-dash-hero-wrap", (h, d) => engenharia.dashboard.hero.render(h, d)) && ok;
			ok =
				patch(".eng-dash-zona-critica", (h, d) => {
					engenharia.dashboard.attention.render(h, d);
					engenharia.dashboard.attention.bind(h);
				}) && ok;
			ok =
				patch(".eng-dash-next-event-host", (h, d) => {
					engenharia.dashboard.next_event.render(h, d);
					utils.bind_routes(h);
				}) && ok;
			ok =
				patch(".eng-dash-agenda-host", (h, d, p) => {
					engenharia.dashboard.timeline.render(h, d, p);
					utils.bind_routes(h);
				}) && ok;

			if (data.is_manager) {
				ok = patch(".eng-dash-health-host", (h, d) => engenharia.dashboard.health.render(h, d)) && ok;
				ok = patch(".eng-dash-kpis-host", (h, d) => engenharia.dashboard.kpis.render(h, d)) && ok;
				ok =
					patch(".eng-dash-finance-host", (h, d, p) => {
						engenharia.dashboard.financial.render(h, d, p);
					}) && ok;
				ok =
					patch(".eng-dash-lists-host", (h, d, p) => {
						engenharia.dashboard.lists.render_duo(h, d, p);
					}) && ok;
			}

			if (!ok) {
				engenharia.dashboard.render_dashboard($container, data, page, { animate: false });
			}

			utils.restore_scroll(scroll);
		})
		.catch(() => {
			frappe.show_alert({
				message: __("Não foi possível atualizar o período."),
				indicator: "red",
			});
		});
}

function eng_dashboard_refresh_list_sections(page) {
	const $container = page.$container;
	const $agenda = $container.find(".eng-dash-agenda-host");
	const $lists = $container.find(".eng-dash-lists-host");
	const $operational = $container.find(".eng-dash-operational-host");
	if (!$agenda.length && !$lists.length && !$operational.length) return;

	const utils = engenharia.dashboard.utils;
	const scroll = utils.save_scroll($container);

	eng_dashboard_fetch_data(page)
		.then((data) => {
			page.eng_dash_data = data;

			if ($agenda.length) {
				utils.patch_host($agenda, () => {
					engenharia.dashboard.timeline.render($agenda, data, page);
					utils.bind_routes($agenda);
				});
			}
			if ($lists.length) {
				utils.patch_host($lists, () => {
					engenharia.dashboard.lists.render_duo($lists, data, page);
				});
			}
			if ($operational.length) {
				utils.patch_host($operational, () => {
					engenharia.dashboard.operational.render($operational, data, page);
				});
			}

			utils.restore_scroll(scroll);
		})
		.catch(() => {
			frappe.show_alert({
				message: __("Não foi possível atualizar as listas."),
				indicator: "red",
			});
		});
}

frappe.provide("engenharia.dashboard");

engenharia.dashboard.render_dashboard = function ($container, data, page, options = {}) {
	$container.empty();
	const stableClass = options.animate === false ? " eng-dash-content--stable" : "";
	const $content = $(`<div class="eng-dash-content dashboard-content${stableClass}"></div>`).appendTo(
		$container
	);

	const $hero = $('<div class="eng-dash-hero-wrap eng-dash-priority-high"></div>').appendTo($content);
	const $filters = $('<div class="eng-dash-filters-wrap"></div>').appendTo($content);
	const $attentionRow = $('<div class="eng-dash-attention-duo"></div>').appendTo($content);
	const $attention = $('<div class="eng-dash-zona-critica"></div>').appendTo($attentionRow);
	const $nextEvent = $('<div class="eng-dash-next-event-host"></div>').appendTo($attentionRow);
	const $actions = $('<div class="eng-dash-actions-host"></div>').appendTo($content);
	const $agenda = $('<div class="eng-dash-agenda-host"></div>').appendTo($content);
	const $operational = $('<div class="eng-dash-zona-operacional eng-dash-operational-host"></div>').appendTo($content);
	const $financeZone = $('<div class="eng-dash-zona-financeira"></div>').appendTo($content);
	const $financeHead = $('<div class="eng-dash-finance-head"></div>').appendTo($financeZone);
	const $health = $('<div class="eng-dash-health-host"></div>').appendTo($financeHead);
	const $kpis = $('<div class="eng-dash-kpis-host"></div>').appendTo($financeHead);
	const $fin = $('<div class="eng-dash-finance-host"></div>').appendTo($financeZone);
	const $lists = $('<div class="eng-dash-lists-host"></div>').appendTo($content);

	engenharia.dashboard.hero.render($hero, data);
	engenharia.dashboard.filters.render($filters, data, page);
	engenharia.dashboard.quick_actions.render($actions);
	engenharia.dashboard.attention.render($attention, data);
	engenharia.dashboard.next_event.render($nextEvent, data);
	engenharia.dashboard.timeline.render($agenda, data, page);
	engenharia.dashboard.utils.bind_routes($agenda);
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

	$content.children().addClass("eng-dashboard-section");
	$content
		.find(".eng-dash-section, .eng-dash-centro, .eng-dash-saude, .eng-dash-kpi, .eng-dash-fluxo-card")
		.addClass("eng-dashboard-card");

	eng_dashboard_bind_list_limits_once(page);
	eng_dashboard_bind_period_filters_once(page);
	engenharia.dashboard.hero.bind($content);
	engenharia.dashboard.quick_actions.bind($content);
	engenharia.dashboard.attention.bind($content);
};
