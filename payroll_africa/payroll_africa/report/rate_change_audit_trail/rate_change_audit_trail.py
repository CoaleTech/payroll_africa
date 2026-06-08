import json

import frappe
from frappe import _

from payroll_africa.engine.registry import SETTINGS_MAP

# Display-friendly country labels for the report (DRC instead of full name)
_DISPLAY_LABELS = {
	"Congo, The Democratic Republic of the": "DRC",
}


def _display_label(country):
	return _DISPLAY_LABELS.get(country, country)


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "country", "label": _("Country"), "fieldtype": "Data", "width": 120},
		{"fieldname": "doctype_name", "label": _("Settings DocType"), "fieldtype": "Data", "width": 200},
		{"fieldname": "field", "label": _("Field"), "fieldtype": "Data", "width": 200},
		{"fieldname": "old_value", "label": _("Old Value"), "fieldtype": "Data", "width": 150},
		{"fieldname": "new_value", "label": _("New Value"), "fieldtype": "Data", "width": 150},
		{"fieldname": "changed_by", "label": _("Changed By"), "fieldtype": "Link", "options": "User", "width": 180},
		{"fieldname": "changed_on", "label": _("Changed On"), "fieldtype": "Datetime", "width": 180},
	]


def get_data(filters):
	if filters and filters.get("country"):
		filter_country = filters["country"]
		# Accept both display label (DRC) and full name
		reverse_display = {v: k for k, v in _DISPLAY_LABELS.items()}
		canonical = reverse_display.get(filter_country, filter_country)
		if canonical not in SETTINGS_MAP:
			return []
		doctypes = {canonical: SETTINGS_MAP[canonical]}
	else:
		doctypes = dict(SETTINGS_MAP)

	doctype_to_country = {v: k for k, v in doctypes.items()}
	doctype_list = list(doctypes.values())

	conditions = ""
	query_filters = {"doctypes": doctype_list}

	if filters and filters.get("from_date"):
		conditions += " AND v.creation >= %(from_date)s"
		query_filters["from_date"] = filters["from_date"]
	if filters and filters.get("to_date"):
		conditions += " AND v.creation <= %(to_date)s"
		query_filters["to_date"] = filters["to_date"]

	versions = frappe.db.sql(
		"""
		SELECT v.ref_doctype, v.data, v.owner, v.creation
		FROM `tabVersion` v
		WHERE v.ref_doctype IN %(doctypes)s
		"""
		+ conditions
		+ """
		ORDER BY v.creation DESC
		""",
		query_filters,
		as_dict=True,
	)

	data = []
	for version in versions:
		try:
			version_data = json.loads(version.data)
		except (json.JSONDecodeError, TypeError):
			continue

		country = _display_label(doctype_to_country.get(version.ref_doctype, version.ref_doctype))

		for change in version_data.get("changed", []):
			if len(change) >= 3:
				data.append({
					"country": country,
					"doctype_name": version.ref_doctype,
					"field": change[0],
					"old_value": str(change[1]) if change[1] is not None else "",
					"new_value": str(change[2]) if change[2] is not None else "",
					"changed_by": version.owner,
					"changed_on": version.creation,
				})

		for change_type in ("added", "removed"):
			for item in version_data.get(change_type, []):
				if isinstance(item, dict):
					data.append({
						"country": country,
						"doctype_name": version.ref_doctype,
						"field": "{0}: {1}".format(change_type.title(), item.get("doctype", "")),
						"old_value": "" if change_type == "added" else str(item),
						"new_value": str(item) if change_type == "added" else "",
						"changed_by": version.owner,
						"changed_on": version.creation,
					})

		for row_change in version_data.get("row_changed", []):
			if len(row_change) >= 4:
				table_name = row_change[0]
				for field_change in row_change[3]:
					if len(field_change) >= 3:
						data.append({
							"country": country,
							"doctype_name": version.ref_doctype,
							"field": "{0} > {1}".format(table_name, field_change[0]),
							"old_value": str(field_change[1]) if field_change[1] is not None else "",
							"new_value": str(field_change[2]) if field_change[2] is not None else "",
							"changed_by": version.owner,
							"changed_on": version.creation,
						})

	return data
