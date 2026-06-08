/**
 * payroll_africa_sidebar.js
 *
 * Hides sidebar items (section headers and their child links) for countries
 * that are disabled in Payroll Africa Settings.
 *
 * Relies on frappe.boot.payroll_africa_enabled_countries injected by the
 * boot extension — an array of enabled country names e.g. ["Kenya", "Uganda"].
 *
 * DOM facts (Frappe v16):
 *   Each sidebar item is rendered as:
 *     <div class="sidebar-item-container [section-item]"
 *          title="{label}" data-id="{label}" ...>
 *       <div class="standard-sidebar-item [indent]">
 *         <div class="item-anchor section-break"> or <a class="item-anchor">
 *           <span class="sidebar-item-label">{label text}</span>
 *         </div>
 *       </div>
 *       <div class="nested-container">...</div>   <!-- child items live here -->
 *     </div>
 *
 * Matching strategy: a sidebar item is considered country-specific when its
 * .sidebar-item-label text starts with a disabled country name followed by a
 * space (e.g. "Kenya Payroll Settings", "Kenya Reports") OR equals the country
 * name exactly (future-proofing).  The "South Africa" prefix guard prevents
 * "Africa" from matching "South Africa" — we always compare the full country
 * name token followed by a word boundary (space or end-of-string).
 */

(function () {
	"use strict";

	const ALL_COUNTRIES = [
		"Kenya",
		"Uganda",
		"Tanzania",
		"Rwanda",
		"Burundi",
		"Ethiopia",
		"Malawi",
		"Zambia",
		"Mozambique",
		"Angola",
		"Botswana",
		"South Africa",
		"Namibia",
		"Madagascar",
		"Nigeria",
		"Ghana",
		"Ivory Coast",
		"DRC",
		"Egypt",
		"Morocco",
		"Tunisia",
	];

	/**
	 * Returns the set of country names that should be hidden, based on
	 * frappe.boot.payroll_africa_enabled_countries.  If the list is absent or
	 * empty, returns an empty set (nothing hidden).
	 */
	function getDisabledCountries() {
		const enabled = frappe &&
			frappe.boot &&
			Array.isArray(frappe.boot.payroll_africa_enabled_countries)
			? frappe.boot.payroll_africa_enabled_countries
			: [];

		if (enabled.length === 0) {
			return new Set();
		}

		const enabledSet = new Set(enabled);
		return new Set(ALL_COUNTRIES.filter((c) => !enabledSet.has(c)));
	}

	/**
	 * Returns true if the sidebar item label text belongs to a disabled country.
	 * Matches exact name ("Kenya") or name-as-prefix ("Kenya Reports",
	 * "Kenya Payroll Settings").  Multi-word country names like "South Africa"
	 * are compared as a whole token.
	 */
	function isDisabledCountryLabel(labelText, disabledSet) {
		const text = labelText.trim();
		for (const country of disabledSet) {
			if (text === country) return true;
			// prefix match: country name must be followed by a space
			if (text.startsWith(country + " ")) return true;
		}
		return false;
	}

	/**
	 * Walks the rendered sidebar and hides every .sidebar-item-container whose
	 * .sidebar-item-label matches a disabled country prefix.
	 */
	function applyVisibility() {
		const disabled = getDisabledCountries();
		if (disabled.size === 0) return;

		const containers = document.querySelectorAll(".sidebar-item-container");
		containers.forEach((container) => {
			// Skip containers that were already processed in this pass to avoid
			// triggering the MutationObserver repeatedly (display:none is a DOM
			// mutation).  We compare against a data attribute we stamp ourselves.
			const labelEl = container.querySelector(".sidebar-item-label");
			if (!labelEl) return;

			const labelText = labelEl.textContent;
			const shouldHide = isDisabledCountryLabel(labelText, disabled);
			const currentlyHidden = container.style.display === "none";

			if (shouldHide && !currentlyHidden) {
				container.style.display = "none";
			} else if (!shouldHide && currentlyHidden) {
				// Only restore items we hid (check our stamp)
				if (container.dataset.payrollAfricaHidden === "1") {
					container.style.display = "";
					delete container.dataset.payrollAfricaHidden;
				}
			}

			if (shouldHide) {
				container.dataset.payrollAfricaHidden = "1";
			}
		});
	}

	// Debounce helper — collapses rapid-fire MutationObserver callbacks
	function debounce(fn, delay) {
		let timer;
		return function () {
			clearTimeout(timer);
			timer = setTimeout(fn, delay);
		};
	}

	const debouncedApply = debounce(applyVisibility, 50);

	// MutationObserver watches for the sidebar being (re-)rendered.
	// We observe subtree changes on document.body so we catch the initial
	// render as well as re-renders triggered by page navigation.
	const observer = new MutationObserver(function (mutations) {
		// Only re-run when actual sidebar nodes were added or removed.
		const relevant = mutations.some((m) =>
			Array.from(m.addedNodes).some(
				(n) =>
					n.nodeType === Node.ELEMENT_NODE &&
					(n.classList.contains("sidebar-item-container") ||
						n.querySelector(".sidebar-item-container"))
			)
		);
		if (relevant) {
			debouncedApply();
		}
	});

	observer.observe(document.body, { childList: true, subtree: true });

	// Also re-apply on every route change because frappe.app.sidebar.setup()
	// replaces .sidebar-items innerHTML on each navigation.
	if (frappe && frappe.router && typeof frappe.router.on === "function") {
		frappe.router.on("change", function () {
			// Small delay lets sidebar.setup() finish rendering before we scan.
			setTimeout(applyVisibility, 100);
		});
	}

	// Run once immediately in case the sidebar is already rendered by the time
	// this script executes (e.g. hot-reload in development).
	applyVisibility();
})();
