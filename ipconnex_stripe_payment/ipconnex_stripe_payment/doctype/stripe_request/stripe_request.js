var script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@10';
document.head.appendChild(script);


frappe.ui.form.on('Stripe Request', {
    refresh:function(frm){
        $("button[data-fieldname='generate_key']").off("click").on("click",(event)=>{
             console.log("Generate Key")
            
             frappe.call({
                method:"ipconnex_stripe_payment.ipconnex_stripe_payment.payement.generateClientSecret",
                args:{
                    amount:parseInt(frm.doc.requested_amount*100),
                    currency:(""+frm.doc.currency).toLowerCase(),
                    methods:['card']
                },
                callback: function(response) { 
                    if(response.status){
                        frm.set_value({"payment_url":"/process_payment?token="+response.message});
                        if(frm.doc.__unsaved){
                            frm.save();
                        }
	                    Swal.fire({
                            icon: 'success',
                            title: 'Success',
                            text: 'Token Updated ! ',
                          });

                    }else{
                        
                        Swal.fire({
                            icon: 'error',
                            title: 'Fail',
                            text: response.message,
                          });
                    }
                }});
            
            
            })
    },
    request_type:function(frm){   
        frm.set_value({
            "requested_amount":0.00,
            "currency":"CAD",
            "customer":"",
            "sales_invoice":"",
            "sales_order":"",
            "is_supplier":0,
            "allow_card":1,
        });
    },
    sales_invoice:function(frm){
        
        if(frm.doc.sales_invoice ){
             frappe.call({
                method: "frappe.desk.form.load.getdoc",
                args:{
                    doctype:"Sales Invoice",
                    name:frm.doc.sales_invoice
                },
                callback: function(res) { 
                    frm.set_value({
                        "requested_amount":res.docs[0].grand_total,
                        "currency":res.docs[0].currency,
                        "customer":res.docs[0].customer
                    });
                }
            }) 
        }
    },
    sales_order:function(frm){
        if(frm.doc.sales_order ){
            frappe.call({
               method: "frappe.desk.form.load.getdoc",
               args:{
                   doctype:"Sales Order",
                   name:frm.doc.sales_order
               },
               callback: function(res) { 
                   frm.set_value({
                       "requested_amount":res.docs[0].grand_total,
                       "currency":res.docs[0].currency,
                       "customer":res.docs[0].customer
                   });
               }
           }) 
       }
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
