frappe.provide("engenharia.list_filters");

(function () {
	const MOBILE_MAX_WIDTH = 768;
	const enhanced_areas = [];

	function is_mobile_layout() {
		return window.innerWidth < MOBILE_MAX_WIDTH;
	}

	function get_wrapper(filter_area) {
		if (filter_area.standard_filters_wrapper && filter_area.standard_filters_wrapper.length) {
			return filter_area.standard_filters_wrapper;
		}
		if (!filter_area.list_view || !filter_area.list_view.page) {
			return null;
		}
		const $wrapper = filter_area.list_view.page.page_form.find(".standard-filter-section");
		if ($wrapper.length) {
			filter_area.standard_filters_wrapper = $wrapper;
		}
		return $wrapper.length ? $wrapper : null;
	}

	function apply_responsive_filter_layout(filter_area) {
		const $wrapper = get_wrapper(filter_area);
		if (!$wrapper) {
			return false;
		}

		if (is_mobile_layout()) {
			$wrapper.removeClass("engenharia-filters-desktop-visible");
			if (filter_area.standard_filters_visible) {
				$wrapper.addClass("engenharia-filters-mobile-open").show();
			} else {
				$wrapper.removeClass("engenharia-filters-mobile-open").hide();
			}
		} else {
			filter_area.standard_filters_visible = true;
			$wrapper
				.removeClass("engenharia-filters-mobile-open")
				.addClass("engenharia-filters-desktop-visible")
				.show();
		}

		return true;
	}

	function wait_for_wrapper(filter_area, retries) {
		retries = retries || 0;
		if (apply_responsive_filter_layout(filter_area) || retries >= 40) {
			return;
		}
		setTimeout(function () {
			wait_for_wrapper(filter_area, retries + 1);
		}, 100);
	}

	engenharia.list_filters.enhance = function (filter_area) {
		if (!filter_area || filter_area.__engenharia_responsive_enhanced) {
			return;
		}

		filter_area.__engenharia_responsive_enhanced = true;
		enhanced_areas.push(filter_area);

		const _toggle = filter_area.toggle_standard_filter.bind(filter_area);
		filter_area.toggle_standard_filter = function () {
			_toggle();
			apply_responsive_filter_layout(filter_area);
		};

		wait_for_wrapper(filter_area, 0);
	};

	function refresh_all_filter_areas() {
		enhanced_areas.forEach(function (filter_area) {
			if (is_mobile_layout()) {
				filter_area.standard_filters_visible = false;
			}
			apply_responsive_filter_layout(filter_area);
		});
	}

	function patch_base_list() {
		if (!frappe.views || !frappe.views.BaseList) {
			return false;
		}
		if (frappe.views.BaseList.prototype.__engenharia_filter_responsive_patched) {
			return true;
		}

		const _setup_filter_area = frappe.views.BaseList.prototype.setup_filter_area;
		frappe.views.BaseList.prototype.setup_filter_area = function () {
			_setup_filter_area.call(this);
			if (this.filter_area) {
				engenharia.list_filters.enhance(this.filter_area);
			}
		};

		frappe.views.BaseList.prototype.__engenharia_filter_responsive_patched = true;
		return true;
	}

	function ensure_patches(retries) {
		retries = retries || 0;
		const ok = patch_base_list();
		if (!ok && retries < 40) {
			setTimeout(function () {
				ensure_patches(retries + 1);
			}, 250);
		}
	}

	function init() {
		window.addEventListener("resize", frappe.utils.debounce(refresh_all_filter_areas, 200));
		ensure_patches(0);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();
