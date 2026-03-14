import frappe
from frappe.model.document import Document


class PayrollAfricaSettings(Document):
	def on_update(self):
		frappe.publish_realtime("payroll_africa_settings_updated")
		frappe.clear_cache()
