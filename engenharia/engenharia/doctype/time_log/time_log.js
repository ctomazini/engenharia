frappe.ui.form.on("Time Log", {
	refresh(frm) {
		if (!frm.is_new()) {
			if (frm.doc.timer_active) {
				frm.add_custom_button(__("⏹ Parar Timer"), () => frm.events.stop_timer(frm));
				frm.change_custom_button_type(__("⏹ Parar Timer"), null, "danger");
				frm.events._start_visual_timer(frm);
				frm.events._enable_beforeunload(frm);
			} else {
				frm.add_custom_button(__("▶ Iniciar Timer"), () => frm.events.start_timer(frm));
				frm.change_custom_button_type(__("▶ Iniciar Timer"), null, "primary");
				frm.events._stop_visual_timer(frm);
				frm.events._disable_beforeunload(frm);
			}
		} else {
			frm.events._stop_visual_timer(frm);
			frm.events._disable_beforeunload(frm);
			if (frm.doc.project && frm.doc.activity) {
				frm.add_custom_button(
					__("Salvar e Iniciar Timer"),
					() => frm.events.save_and_start_timer(frm),
					__("Timer")
				);
				frm.change_custom_button_type(__("Salvar e Iniciar Timer"), __("Timer"), "primary");
			}
		}
	},

	save_and_start_timer(frm) {
		if (!frm.doc.duration_minutes) {
			frm.set_value("duration_minutes", 0);
		}
		frm.save().then(function () {
			frm.events.start_timer(frm);
		});
	},

	start_timer(frm) {
		frappe.call({
			method: "start_timer",
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Iniciando timer..."),
			callback() {
				frm.reload_doc().then(function () {
					if (engenharia.timer_global) {
						engenharia.timer_global.refresh();
					}
				});
			},
		});
	},

	stop_timer(frm) {
		frappe.call({
			method: "stop_timer",
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Parando timer..."),
			callback(r) {
				if (r.message) {
					var secs = Math.round(r.message.elapsed_seconds || 0);
					var h = Math.floor(secs / 3600);
					var m = Math.floor((secs % 3600) / 60);
					var s = secs % 60;
					frappe.show_alert(
						{
							message: __("Timer parado: {0}h {1}m {2}s adicionados", [h, m, s]),
							indicator: "green",
						},
						5
					);
				}
				frm.reload_doc().then(function () {
					if (engenharia.timer_global) {
						engenharia.timer_global.refresh();
					}
				});
			},
		});
	},

	_start_visual_timer(frm) {
		if (frm._timer_interval) {
			clearInterval(frm._timer_interval);
		}

		var wrapper = frm.fields_dict.timer_display && frm.fields_dict.timer_display.$wrapper;
		if (!wrapper || !frm.doc.timer_started_at) {
			return;
		}

		var start = frappe.datetime.str_to_obj(frm.doc.timer_started_at);

		function pad(n) {
			return String(n).padStart(2, "0");
		}

		function update() {
			var now = new Date();
			var diff = Math.floor((now - start) / 1000);
			if (diff < 0) {
				diff = 0;
			}
			var h = Math.floor(diff / 3600);
			var m = Math.floor((diff % 3600) / 60);
			var s = diff % 60;
			wrapper.html(
				'<div class="time-log-timer">' +
					'<span class="time-log-timer-dot"></span>' +
					'<span class="time-log-timer-clock">' +
					pad(h) +
					":" +
					pad(m) +
					":" +
					pad(s) +
					"</span>" +
					"</div>" +
					"<style>" +
					".time-log-timer {" +
					"display:flex;align-items:center;gap:10px;" +
					"font-size:32px;font-weight:700;" +
					"font-family:var(--font-stack-monospace, 'Courier New', monospace);" +
					"color:var(--text-color);padding:12px 0;" +
					"}" +
					".time-log-timer-dot {" +
					"display:inline-block;width:10px;height:10px;border-radius:50%;" +
					"background:var(--red-500);" +
					"animation:time-log-pulse 1.5s ease-in-out infinite;" +
					"}" +
					"@keyframes time-log-pulse {" +
					"0%,100%{opacity:1}50%{opacity:0.3}" +
					"}" +
					"</style>"
			);
		}

		update();
		frm._timer_interval = setInterval(update, 1000);
	},

	_stop_visual_timer(frm) {
		if (frm._timer_interval) {
			clearInterval(frm._timer_interval);
			frm._timer_interval = null;
		}
		var wrapper = frm.fields_dict.timer_display && frm.fields_dict.timer_display.$wrapper;
		if (wrapper) {
			wrapper.html("");
		}
	},

	_enable_beforeunload(frm) {
		if (!frm._beforeunload_handler) {
			frm._beforeunload_handler = function (e) {
				e.preventDefault();
				e.returnValue = __("Timer em execução! Tem certeza que deseja sair?");
				return e.returnValue;
			};
			window.addEventListener("beforeunload", frm._beforeunload_handler);
		}
	},

	_disable_beforeunload(frm) {
		if (frm._beforeunload_handler) {
			window.removeEventListener("beforeunload", frm._beforeunload_handler);
			frm._beforeunload_handler = null;
		}
	},

	before_load(frm) {
		frm.events._stop_visual_timer(frm);
		frm.events._disable_beforeunload(frm);
	},
});
