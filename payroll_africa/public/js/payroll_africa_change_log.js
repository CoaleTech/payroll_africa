/**
 * Enhanced Change Log Renderer for Payroll Africa
 *
 * Intercepts Frappe's default change_log rendering for payroll_africa entries
 * and renders them with a styled headline banner and categorized badges.
 *
 * Markdown convention:
 *   # Headline
 *   Description paragraph
 *   ## New / ## Improved / ## Fixed
 *   - Item 1
 *   - Item 2
 */
$(document).on("app_ready", function () {
	if (!frappe.boot.change_log || !Array.isArray(frappe.boot.change_log)) return;

	// Find payroll_africa entries
	const pa_entries = [];
	const other_entries = [];

	frappe.boot.change_log.forEach(function (entry) {
		if (entry.title === "Payroll Africa") {
			pa_entries.push(entry);
		} else {
			other_entries.push(entry);
		}
	});

	if (!pa_entries.length) return;

	// Remove payroll_africa from the default change_log so Frappe doesn't render it
	frappe.boot.change_log = other_entries;

	// Parse and render our custom dialog
	const content = build_payroll_africa_changelog(pa_entries);
	if (!content) return;

	const dialog = frappe.msgprint({
		message: content,
		title: __("Payroll Africa \u2014 What's New"),
		wide: true,
	});
	dialog.keep_open = true;
	dialog.custom_onhide = function () {
		frappe.call({
			method: "frappe.utils.change_log.update_last_known_versions",
		});
	};
});

function build_payroll_africa_changelog(entries) {
	let html = "";

	entries.forEach(function (entry) {
		// Each entry.change_log is an array of [version_string, markdown_text]
		if (!entry.change_log || !entry.change_log.length) return;

		entry.change_log.forEach(function (version_info) {
			if (!version_info || !version_info[1]) return;

			const md = version_info[1];
			const parsed = parse_changelog_md(md);

			// Headline banner
			html += '<div class="pa-changelog-entry">';
			html +=
				'<div class="pa-changelog-banner">' +
				'<div class="pa-changelog-banner-content">' +
				'<img src="/assets/payroll_africa/icons/africa.svg" class="pa-changelog-icon" />' +
				"<div>" +
				'<h3 class="pa-changelog-headline">' +
				frappe.utils.escape_html(parsed.headline) +
				"</h3>" +
				'<span class="pa-changelog-version">v' +
				frappe.utils.escape_html(version_info[0]) +
				"</span>" +
				"</div>" +
				"</div>" +
				"</div>";

			// Description
			if (parsed.description) {
				html +=
					'<p class="pa-changelog-description">' +
					frappe.utils.escape_html(parsed.description) +
					"</p>";
			}

			// Categories
			const categories = [
				{ key: "new", label: "New", css: "pa-badge-new" },
				{ key: "improved", label: "Improved", css: "pa-badge-improved" },
				{ key: "fixed", label: "Fixed", css: "pa-badge-fixed" },
			];

			categories.forEach(function (cat) {
				const items = parsed[cat.key];
				if (!items || !items.length) return;
				html += '<div class="pa-changelog-category">';
				html +=
					'<span class="pa-changelog-badge ' +
					cat.css +
					'">' +
					cat.label +
					"</span>";
				html += "<ul>";
				items.forEach(function (item) {
					html +=
						"<li>" + frappe.utils.escape_html(item) + "</li>";
				});
				html += "</ul>";
				html += "</div>";
			});

			html += "</div>";
		});
	});

	return html;
}

function parse_changelog_md(md) {
	const result = { headline: "", description: "", new: [], improved: [], fixed: [] };
	const lines = md.split("\n");
	let current_section = null;

	for (let i = 0; i < lines.length; i++) {
		const line = lines[i].trim();

		// H1 = headline
		if (line.startsWith("# ") && !line.startsWith("## ")) {
			result.headline = line.replace(/^#\s+/, "");
			continue;
		}

		// H2 = section
		if (line.startsWith("## ")) {
			const section = line.replace(/^##\s+/, "").toLowerCase();
			if (section === "new") current_section = "new";
			else if (section === "improved") current_section = "improved";
			else if (section === "fixed") current_section = "fixed";
			else current_section = null;
			continue;
		}

		// List items
		if (line.startsWith("- ") && current_section) {
			result[current_section].push(line.replace(/^-\s+/, ""));
			continue;
		}

		// Description = first non-empty line after headline, before any ## section
		if (line && !current_section && result.headline && !result.description) {
			result.description = line;
		}
	}

	return result;
}
