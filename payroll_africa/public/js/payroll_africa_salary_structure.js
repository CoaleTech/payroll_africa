// Filter Salary Component link fields in Salary Structure to only show
// components for countries enabled in Payroll Africa Settings.
frappe.ui.form.on("Salary Structure", {
	setup(frm) {
		const enabled = frappe.boot.payroll_africa_enabled_countries || [];
		if (!enabled.length) return;

		// Build list of disabled country suffixes for component filtering.
		// Salary components are named like "PAYE", "NSSF Employee UG", "PAYE TZ" etc.
		// Components without a country suffix are Kenya-specific (no suffix = Kenya).
		const all_countries = {
			Kenya: ["", "KE"],
			Uganda: ["UG"],
			Tanzania: ["TZ"],
			Rwanda: ["RW"],
			Burundi: ["BI"],
			Zambia: ["ZM"],
			Malawi: ["MW"],
			"Congo, The Democratic Republic of the": ["CD"],
			Nigeria: ["NG"],
			Mozambique: ["MZ"],
			Angola: ["AO"],
		};

		// Collect suffixes of DISABLED countries
		const disabled_suffixes = [];
		for (const [country, suffixes] of Object.entries(all_countries)) {
			if (!enabled.includes(country)) {
				disabled_suffixes.push(...suffixes);
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
