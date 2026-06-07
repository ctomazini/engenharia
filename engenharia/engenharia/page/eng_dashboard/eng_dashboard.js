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

	if (!page.eng_dash_list_limits) {
		page.eng_dash_list_limits = engenharia.dashboard?.utils?.default_list_limits?.() || {};
	}

	frappe
		.xcall("engenharia.dashboard_api.get_dashboard_data", {
			period_days: page.period_days,
			list_limits: page.eng_dash_list_limits,
		})
		.then((data) => {
			page.eng_dash_data = data;

			const $hero = $container.find(".eng-dash-hero-wrap");
			if ($hero.length) {
				engenharia.dashboard.hero.render($hero, data);
			}

			const $filters = $container.find(".eng-dash-filters-wrap");
			if ($filters.length) {
				engenharia.dashboard.filters.render($filters, data, page);
			}

			const $attention = $container.find(".eng-dash-zona-critica");
			if ($attention.length) {
				engenharia.dashboard.attention.render($attention, data);
				engenharia.dashboard.attention.bind($attention);
			}

			const $nextEvent = $container.find(".eng-dash-next-event-host");
			if ($nextEvent.length) {
				engenharia.dashboard.next_event.render($nextEvent, data);
				engenharia.dashboard.utils.bind_routes($nextEvent);
			}

			const $agenda = $container.find(".eng-dash-agenda-host");
			if ($agenda.length) {
				engenharia.dashboard.timeline.render($agenda, data, page);
				engenharia.dashboard.utils.bind_routes($agenda);
			}

			if (data.is_manager) {
				const $health = $container.find(".eng-dash-health-host");
				if ($health.length) {
					engenharia.dashboard.health.render($health, data);
				}

				const $kpis = $container.find(".eng-dash-kpis-host");
				if ($kpis.length) {
					engenharia.dashboard.kpis.render($kpis, data);
				}

				const $fin = $container.find(".eng-dash-finance-host");
				if ($fin.length) {
					engenharia.dashboard.financial.render($fin, data, page);
				}

				const $lists = $container.find(".eng-dash-lists-host");
				if ($lists.length) {
					engenharia.dashboard.lists.render_duo($lists, data, page);
				}
			}
		})
		.catch(() => {
			frappe.show_alert({
				message: __("Não foi possível atualizar o período."),
				indicator: "red",
			});
		});
}

function eng_dashboard_refresh_list_sections(page) {
	const $agenda = page.$container.find(".eng-dash-agenda-host");
	const $lists = page.$container.find(".eng-dash-lists-host");
	const $operational = page.$container.find(".eng-dash-operational-host");
	if (!$agenda.length && !$lists.length && !$operational.length) return;

	if (!page.eng_dash_list_limits) {
		page.eng_dash_list_limits = engenharia.dashboard?.utils?.default_list_limits?.() || {};
	}

	frappe
		.xcall("engenharia.dashboard_api.get_dashboard_data", {
			period_days: page.period_days,
			list_limits: page.eng_dash_list_limits,
		})
		.then((data) => {
			page.eng_dash_data = data;
			if ($agenda.length) {
				$agenda.empty();
				engenharia.dashboard.timeline.render($agenda, data, page);
			}
			if ($lists.length) {
				$lists.empty();
				engenharia.dashboard.lists.render_duo($lists, data, page);
			}
			if ($operational.length) {
				$operational.empty();
				engenharia.dashboard.operational.render($operational, data, page);
			}
		})
		.catch(() => {
			frappe.show_alert({
				message: __("Não foi possível atualizar as listas."),
				indicator: "red",
			});
		});
}

frappe.provide("engenharia.dashboard");

engenharia.dashboard.render_dashboard = function ($container, data, page) {
	$container.empty();
	const $content = $('<div class="eng-dash-content dashboard-content"></div>').appendTo($container);

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
