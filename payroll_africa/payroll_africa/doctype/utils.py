import frappe
from frappe import _
from frappe.utils import flt


def validate_paye_bands(doc):
	"""Validate PAYE bands are sequential with non-negative rates."""
	if not hasattr(doc, "paye_bands") or not doc.paye_bands:
		return

	for i, band in enumerate(doc.paye_bands):
		if flt(band.rate) < 0 or flt(band.rate) > 100:
			frappe.throw(
				_("Row {0}: Rate must be between 0 and 100").format(i + 1)
			)
		if flt(band.from_amount) < 0:
			frappe.throw(
				_("Row {0}: From Amount cannot be negative").format(i + 1)
			)
		if flt(band.to_amount) < 0:
			frappe.throw(
				_("Row {0}: To Amount cannot be negative").format(i + 1)
			)

	# Check bands are ordered by from_amount
	for i in range(1, len(doc.paye_bands)):
		prev = doc.paye_bands[i - 1]
		curr = doc.paye_bands[i]
		if flt(curr.from_amount) <= flt(prev.from_amount):
			frappe.throw(
				_("Row {0}: From Amount must be greater than previous band").format(i + 1)
			)
