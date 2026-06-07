frappe.provide("engenharia.reports");

/** Expande colunas para preencher a largura do painel (frappe-datatable layout fluid). */
engenharia.reports.get_datatable_options = function (options) {
	options.layout = "fluid";
	return options;
};

function engenharia_patch_query_report_datatable() {
	if (engenharia.reports._datatable_patched || !frappe.views?.QueryReport) {
		return;
	}
	engenharia.reports._datatable_patched = true;

	const proto = frappe.views.QueryReport.prototype;
	const render_datatable = proto.render_datatable;

	proto.render_datatable = function () {
		this.report_settings = this.report_settings || {};
		if (!this.report_settings.get_datatable_options) {
			this.report_settings.get_datatable_options = engenharia.reports.get_datatable_options;
		}
		render_datatable.call(this);
		if (this.datatable?.style?.setDimensions) {
			this.datatable.style.setDimensions();
		}
	};
}

engenharia_patch_query_report_datatable();
$(document).on("app_ready", engenharia_patch_query_report_datatable);
