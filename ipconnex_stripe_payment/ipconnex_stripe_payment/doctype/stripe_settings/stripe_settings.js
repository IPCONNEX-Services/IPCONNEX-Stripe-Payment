// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stripe Settings', {
    refresh:function(frm){
        frm.set_query("pay_to", function() {
            return {
                "filters": {
                    "is_group": 0
                }
            };
        });
    }
});
