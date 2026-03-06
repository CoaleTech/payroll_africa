frappe.query_reports["MRA P9 Deduction Certificate"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			default: frappe.defaults.get_user_default("Company"),
			get_query: function() {
				return { filters: { country: "Malawi" } };
			},
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
			reqd: 1,
		},
		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			reqd: 1,
		},
	],
	onload: function(report) {
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Company",
				filters: { country: "Malawi" },
				fields: ["name"],
				limit_page_length: 1,
			},
			callback: function(r) {
				if (r.message && r.message.length) {
					var company_filter = report.get_filter("company");
					if (company_filter) {
						company_filter.set_value(r.message[0].name);
					}
				}
			},
		});
	},
};
