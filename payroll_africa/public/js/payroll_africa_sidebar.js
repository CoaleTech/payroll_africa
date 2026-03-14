// Dynamic sidebar filtering for Payroll Africa.
// Hides country settings, reports, and region sections for disabled countries.
// Listens for real-time updates when Payroll Africa Settings are changed.

frappe.provide("payroll_africa.sidebar");

payroll_africa.sidebar = (function () {
	// Maps sidebar label prefix to bootinfo country name.
	const LABEL_TO_COUNTRY = {
		Kenya: "Kenya",
		Uganda: "Uganda",
		Tanzania: "Tanzania",
		Rwanda: "Rwanda",
		Burundi: "Burundi",
		Zambia: "Zambia",
		Malawi: "Malawi",
		DRC: "Congo, The Democratic Republic of the",
		Nigeria: "Nigeria",
		Mozambique: "Mozambique",
		Angola: "Angola",
	};

	// Region sections and which label prefixes they contain.
	const REGIONS = {
		"East Africa": ["Kenya", "Uganda", "Tanzania", "Rwanda", "Burundi"],
		"Southern Africa": ["Malawi", "Zambia", "Mozambique", "Angola"],
		"West & Central Africa": ["Nigeria", "DRC"],
	};

	function get_enabled_labels() {
		const enabled_countries = frappe.boot.payroll_africa_enabled_countries || [];
		const enabled = new Set();
		for (const [label, country] of Object.entries(LABEL_TO_COUNTRY)) {
			if (enabled_countries.includes(country)) {
				enabled.add(label);
			}
		}
		return enabled;
	}

	function apply_filter() {
		const enabled = get_enabled_labels();

		// Hide/show country settings links and country report sections.
		for (const label of Object.keys(LABEL_TO_COUNTRY)) {
			const settings_item = document.querySelector(
				`.sidebar-item-container[item-name="${label} Payroll Settings"]`
			);
			const reports_item = document.querySelector(
				`.sidebar-item-container[item-name="${label} Reports"]`
			);
			const visible = enabled.has(label);

			if (settings_item) {
				settings_item.style.display = visible ? "" : "none";
			}
			if (reports_item) {
				reports_item.style.display = visible ? "" : "none";
			}
		}

		// Hide/show region section headers when all children are disabled.
		for (const [region, children] of Object.entries(REGIONS)) {
			const region_item = document.querySelector(
				`.sidebar-item-container[item-name="${region}"]`
			);
			if (region_item) {
				const any_visible = children.some((label) => enabled.has(label));
				region_item.style.display = any_visible ? "" : "none";
			}
		}
	}

	function refresh_from_server() {
		frappe.xcall("payroll_africa.boot.get_enabled_countries").then(function (countries) {
			frappe.boot.payroll_africa_enabled_countries = countries;
			apply_filter();
		});
	}

	function init() {
		// Apply filter once sidebar renders (may be delayed).
		if (document.readyState === "complete") {
			setTimeout(apply_filter, 500);
		} else {
			$(window).on("load", function () {
				setTimeout(apply_filter, 500);
			});
		}

		// Re-apply on page navigation (sidebar may re-render).
		$(document).on("page-change", apply_filter);

		// Listen for real-time updates when settings change.
		frappe.realtime.on("payroll_africa_settings_updated", refresh_from_server);

		// Observe sidebar for dynamic re-renders (Vue reactivity).
		const observer = new MutationObserver(function () {
			apply_filter();
		});

		function observe_sidebar() {
			const sidebar = document.querySelector(".sidebar-items");
			if (sidebar) {
				observer.observe(sidebar, { childList: true, subtree: true });
				apply_filter();
			} else {
				setTimeout(observe_sidebar, 500);
			}
		}

		observe_sidebar();
	}

	return { init: init, apply_filter: apply_filter };
})();

payroll_africa.sidebar.init();
