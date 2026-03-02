import frappe
from frappe.model.document import Document


class ZambiaPayrollSettings(Document):
	def validate(self):
		from payroll_africa.payroll_africa.doctype.utils import validate_paye_bands
		validate_paye_bands(self)

	def on_update(self):
		# Clear calculator cache when settings change
		from payroll_africa.engine.registry import clear_cache
		clear_cache()
		frappe.clear_cache(doctype="Zambia Payroll Settings")
