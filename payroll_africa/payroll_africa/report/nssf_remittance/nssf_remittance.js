frappe.query_reports["NSSF Remittance"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			default: frappe.defaults.get_user_default("Company"),
			get_query: function() {
				return { filters: { country: "Kenya" } };
			},
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.get_today(),
		},
	],
	onload: function(report) {
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Company",
				filters: { country: "Kenya" },
				fields: ["name"],
				limit_page_length: 0,
			},
			callback: function(r) {
				var company_filter = report.get_filter("company");
				var names = (r.message || []).map(function(c) { return c.name; });
				// Keep the user's default company when it is in this country; else pick the first one.
				if (company_filter && names.length && names.indexOf(company_filter.get_value()) === -1) {
					company_filter.set_value(names[0]);
				}
			},
		});
	},
};
