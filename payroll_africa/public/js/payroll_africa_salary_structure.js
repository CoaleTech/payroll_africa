// Filter Salary Component link fields in Salary Structure to only show
// components for countries enabled in Payroll Africa Settings.
frappe.ui.form.on("Salary Structure", {
	setup(frm) {
		const enabled = frappe.boot.payroll_africa_enabled_countries || [];
		// suffix_map is injected by payroll_africa.boot.extend_bootinfo and covers
		// all 54 supported countries.  Fall back to empty so the form still works
		// on older boot payloads.
		const suffix_map = frappe.boot.payroll_africa_country_suffix_map || {};
		if (!enabled.length || !Object.keys(suffix_map).length) return;

		// Collect the ISO suffix of every DISABLED country.  Salary components
		// are named like "PAYE", "NSSF Employee UG", "PAYE TZ" – the trailing
		// ISO code is the suffix.  Kenya components carry no suffix ("").
		const disabled_suffixes = [];
		for (const [country, suffix] of Object.entries(suffix_map)) {
			if (!enabled.includes(country)) {
				disabled_suffixes.push(suffix);
			}
		}

		if (!disabled_suffixes.length) return;

		const query_opts = {
			query: "payroll_africa.api.get_filtered_salary_components",
			filters: { disabled_suffixes: disabled_suffixes },
		};

		frm.set_query("salary_component", "deductions", function () {
			return query_opts;
		});

		frm.set_query("salary_component", "earnings", function () {
			return query_opts;
		});
	},
});
