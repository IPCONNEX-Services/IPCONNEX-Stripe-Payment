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
        if(frm.doc.customer && cur_frm.doc.request_type=="Customer" ){
	        frappe.call({
                    method: "frappe.desk.form.load.getdoc",
                    args:{
                        doctype:"Customer",
                        name:frm.doc.customer
                    },
                    callback: function(res_customer) {
                        var dettes=0.00;
                        frappe.call({
                            method: "frappe.desk.form.load.getdoc",
                            args:{
                                doctype:"Supplier",
                                name:frm.doc.customer
                            },
                            callback: function(res_supplier) {
                                    if(res_supplier["docs"]  && frm.doc.is_supplier ){
                                        dettes=(Math.round(res_customer["docs"][0]["__onload"]["dashboard_info"][0]["total_unpaid"]*100)-Math.round(res_supplier["docs"][0]["__onload"]["dashboard_info"][0]["total_unpaid"]*100) )/100 ;
                                    }else{
                                        try{
                                            dettes=Math.round(res_customer["docs"][0]["__onload"]["dashboard_info"][0]["total_unpaid"]*100)/100 ;
                                        }catch(error){
                                        }
                                    }
                                    frm.set_value({"requested_amount":dettes});
                                    }
                            });
                    }
            });
	    }
    },
    is_supplier:function(frm){
        if(frm.doc.customer  && cur_frm.doc.request_type=="Customer" ){
	        frappe.call({
                    method: "frappe.desk.form.load.getdoc",
                    args:{
                        doctype:"Customer",
                        name:frm.doc.custome
                    },
                    callback: function(res_customer) {
                        var dettes=0.00;
                        frappe.call({
                            method: "frappe.desk.form.load.getdoc",
                            args:{
                                doctype:"Supplier",
                                name:frm.doc.customer
                            },
                            callback: function(res_supplier) {
                                    if(res_supplier["docs"] && frm.doc.is_supplier ){
                                        dettes=(Math.round(res_customer["docs"][0]["__onload"]["dashboard_info"][0]["total_unpaid"]*100)-Math.round(res_supplier["docs"][0]["__onload"]["dashboard_info"][0]["total_unpaid"]*100) )/100 ;
                                    }else{
                                        try{
                                            dettes=Math.round(res_customer["docs"][0]["__onload"]["dashboard_info"][0]["total_unpaid"]*100)/100 ;
                                        }catch(error){
                                        }
                                    }
                                    frm.set_value({"requested_amount":dettes});
                                    }
                            });
                    }
            });
	    }
    },
});
