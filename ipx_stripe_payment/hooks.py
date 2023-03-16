# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "ipx_stripe_payment"
app_title = "IPCONNEX Stripe Payment"
app_publisher = "Frappe"
app_description = "A Stripe Payment module created by IPCONNEX"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "voip@ipconnex.com"
app_license = "MIT"


# include js in doctype views
doctype_js = {
	"Sales Invoice" : "public/js/payement.js",
    "Stripe Settings":"public/js/payement.js",
    "Payment Method":"public/js/payement.js",
}

# Scheduled Tasks
# ---------------

scheduler_events = {
}


