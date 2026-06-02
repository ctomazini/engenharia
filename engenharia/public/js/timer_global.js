frappe.provide("engenharia.timer_global");

(function () {
	var WIDGET_ID = "engenharia-timer-global";
	var DOCTYPE = "Time Log";
	var SYNC_MS = 45000;
	var API = "engenharia.engenharia.doctype.time_log.time_log.get_active_user_timer";

	var state = null;
	var tickInterval = null;
	var syncInterval = null;
	var syncing = false;
	var syncDisabled = false;

	function pad(n) {
		return String(n).padStart(2, "0");
	}

	function formatElapsed(startStr) {
		if (!startStr) return "00:00:00";
		var start = frappe.datetime.str_to_obj(startStr);
		var diff = Math.floor((new Date() - start) / 1000);
		if (diff < 0) diff = 0;
		var h = Math.floor(diff / 3600);
		var m = Math.floor((diff % 3600) / 60);
		var s = diff % 60;
		return pad(h) + ":" + pad(m) + ":" + pad(s);
	}

	function timerIcon() {
		try {
			return frappe.utils.icon("clock", "sm") || "";
		} catch (e) {
			return "⏱";
		}
	}

	function canUseTimer() {
		return (
			frappe.session.user !== "Guest" &&
			frappe.model &&
			typeof frappe.model.can_read === "function" &&
			frappe.model.can_read(DOCTYPE)
		);
	}

	function isPermissionError(err) {
		if (!err) return false;
		if (typeof err === "object") {
			if (err.httpStatus === 403 || err.status === 403) return true;
			if (err.exc_type === "PermissionError") return true;
		}
		var msg = String(err.message || err._error_message || err || "");
		return (
			msg.indexOf("403") !== -1 ||
			msg.indexOf("Not permitted") !== -1 ||
			msg.indexOf("not whitelisted") !== -1 ||
			msg.indexOf("Not Allowed") !== -1
		);
	}

	function stopSyncLoop() {
		if (syncInterval) {
			clearInterval(syncInterval);
			syncInterval = null;
		}
	}

	function disableSync(reason) {
		syncDisabled = true;
		stopSyncLoop();
		state = null;
		stopTicking();
		renderWidget();
		if (reason && frappe.session.user !== "Guest") {
			console.debug("engenharia.timer_global: sync desativado —", reason);
		}
	}

	function injectStyles() {
		if (document.getElementById("engenharia-timer-global-styles")) return;
		var style = document.createElement("style");
		style.id = "engenharia-timer-global-styles";
		style.textContent =
			"#engenharia-timer-global {" +
			"position:fixed;" +
			"left:16px;" +
			"bottom:calc(16px + env(safe-area-inset-bottom, 0px));" +
			"display:none;" +
			"align-items:center;" +
			"gap:8px;" +
			"padding:10px 14px;" +
			"border-radius:999px;" +
			"border:1px solid color-mix(in srgb, var(--red-500) 35%, var(--border-color));" +
			"background:color-mix(in srgb, var(--red-500) 12%, var(--card-bg));" +
			"color:var(--text-color);" +
			"font-size:13px;" +
			"font-weight:600;" +
			"cursor:pointer;" +
			"box-shadow:var(--shadow-md, 0 4px 12px rgba(0,0,0,.15));" +
			"z-index:9998;" +
			"max-width:min(320px, calc(100vw - 32px));" +
			"transition:transform .18s ease, box-shadow .18s ease;" +
			"}" +
			"#engenharia-timer-global:hover {" +
			"transform:translateY(-1px);" +
			"box-shadow:var(--shadow-lg, 0 6px 16px rgba(0,0,0,.2));" +
			"}" +
			"#engenharia-timer-global .eng-timer-dot {" +
			"width:8px;height:8px;border-radius:50%;flex-shrink:0;" +
			"background:var(--red-500);" +
			"animation:eng-timer-pulse 1.5s ease-in-out infinite;" +
			"}" +
			"#engenharia-timer-global .eng-timer-clock {" +
			"font-family:var(--font-stack-monospace, 'Courier New', monospace);" +
			"font-variant-numeric:tabular-nums;" +
			"}" +
			"#engenharia-timer-global .eng-timer-label {" +
			"overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" +
			"color:var(--text-muted);font-weight:500;" +
			"}" +
			"@keyframes eng-timer-pulse {" +
			"0%,100%{opacity:1}50%{opacity:.35}" +
			"}";
		document.head.appendChild(style);
	}

	function ensureWidget() {
		injectStyles();
		var el = document.getElementById(WIDGET_ID);
		if (el) return el;

		el = document.createElement("button");
		el.id = WIDGET_ID;
		el.type = "button";
		el.title = __("Timer em execução — clique para abrir o registro");
		el.onclick = function () {
			if (state && state.name) {
				frappe.set_route("Form", DOCTYPE, state.name);
			}
		};
		document.body.appendChild(el);
		return el;
	}

	function renderWidget() {
		var el = ensureWidget();
		if (!state || !state.timer_started_at) {
			el.style.display = "none";
			return;
		}

		el.style.display = "inline-flex";
		var clock = formatElapsed(state.timer_started_at);
		var label = frappe.utils.escape_html(state.activity || state.name || "");
		el.innerHTML =
			'<span class="eng-timer-dot"></span>' +
			'<span class="eng-timer-icon">' +
			timerIcon() +
			"</span>" +
			'<span class="eng-timer-clock">' +
			clock +
			"</span>" +
			(label ? '<span class="eng-timer-label">' + label + "</span>" : "");
	}

	function startTicking() {
		if (tickInterval) return;
		tickInterval = setInterval(renderWidget, 1000);
	}

	function stopTicking() {
		if (tickInterval) {
			clearInterval(tickInterval);
			tickInterval = null;
		}
	}

	function applyState(data) {
		if (data && data.name && data.timer_started_at) {
			state = data;
			startTicking();
		} else {
			state = null;
			stopTicking();
		}
		renderWidget();
	}

	function syncFromServer() {
		if (syncDisabled || !canUseTimer() || syncing) return;
		syncing = true;
		frappe.call({
			method: API,
			quiet: true,
			no_spinner: true,
			callback: function (r) {
				applyState(r.message);
			},
			error: function (err) {
				if (isPermissionError(err)) {
					disableSync("sem permissão para Time Log");
					return;
				}
			},
			always: function () {
				syncing = false;
			},
		});
	}

	function ensureSyncLoop() {
		if (syncInterval || syncDisabled || !canUseTimer()) return;
		syncFromServer();
		syncInterval = setInterval(syncFromServer, SYNC_MS);
	}

	engenharia.timer_global = {
		refresh: syncFromServer,
	};

	frappe.after_ajax(function () {
		if (canUseTimer()) {
			ensureSyncLoop();
		}
	});

	$(document).on("page-change", function () {
		if (canUseTimer() && !syncDisabled && !state) {
			syncFromServer();
		}
	});
})();
