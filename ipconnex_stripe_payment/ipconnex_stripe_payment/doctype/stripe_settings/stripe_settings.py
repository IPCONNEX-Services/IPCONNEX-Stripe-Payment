
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document



class StripeSettings(Document):
    def get(self, *args, **kwargs):
        if frappe.session.user == "Administrator" or frappe.local.request_ip.startswith("127.0.0"):
            pass
        else: 	
            self.secret_key = "*"*len(self.secret_key)
        return super().get(*args, **kwargs)
	