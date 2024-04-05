// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stripe Request', {
    refresh:function(frm){
        $("button[data-fieldname='generate_key']").off("click").on("click",(event)=>{
             console.log("Generate Key")})
    },
    sales_invoice:function(frm){
             console.log("sales_invoice changed")
    },
    sales_order:function(frm){
             console.log("sales_order changed")
    },
    customer:function(frm){
        console.log("customer changed")
    },
    is_supplier:function(frm){
        console.log("is supplier changed")
    },
});
