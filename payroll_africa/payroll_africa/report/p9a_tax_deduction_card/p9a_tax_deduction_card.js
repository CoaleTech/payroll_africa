frappe.query_reports["P9A Tax Deduction Card"] = {
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
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
			reqd: 0,
			get_query: function () {
				return {
					filters: {
						company: frappe.query_report.get_filter_value("company"),
					},
				};
			},
		},
		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			reqd: 1,
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
		},
	],
	onload: function(report) {
		// Prefer the user's own default company when it is already a Kenya entity.
		// The old behaviour (always pick the first alphabetical Kenya company) caused
		// the wrong company to be pre-selected for users whose default company differs
		// from the alphabetically-first Kenya entity.
		var user_company = frappe.defaults.get_user_default("Company");
		if (user_company) {
			frappe.db.get_value("Company", user_company, "country", function(val) {
				if (val && val.country === "Kenya") {
					var f = report.get_filter("company");
					if (f) f.set_value(user_company);
				} else {
					_set_first_kenya_company(report);
				}
			});
		} else {
			_set_first_kenya_company(report);
		}
	},
};

function _set_first_kenya_company(report) {
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Company",
			filters: { country: "Kenya" },
			fields: ["name"],
			limit_page_length: 1,
		},
		callback: function(r) {
			if (r.message && r.message.length) {
				var f = report.get_filter("company");
				if (f) f.set_value(r.message[0].name);
			}
			// If no Kenya company exists, leave the filter empty so the report
			// opens without throwing "Filter missing".
		},
	});
}
