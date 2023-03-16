
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class StripeSettings(Document):
	def get(self, *args, **kwargs):
		# Check if the user is an administrator or the request is executed by Frappe ERP
		if frappe.session.user == "Administrator" or frappe.local.request_ip.startswith("127.0.0"):
			# Allow the "sensitive_info" attribute to be visible
			pass
		else:
			# Hide the "secret_key" attribute from non-administrators or external requests
			self.secret_key = "*"*len(self.secret_key)

		# Call the original "get" method
		return super().get(*args, **kwargs)
