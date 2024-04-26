    frappe.ui.form.on('Sales Invoice', {
        refresh: function(frm) {
            frm.add_custom_button(__('Pay Invoice'), function(event) {
                $('button[data-label="Pay%20Invoice"]').prop('disabled', true);

                if(frm.doc.status !== 'Unpaid' && frm.doc.status !== 'Overdue') {
                    frappe.msgprint('This invoice is ' + frm.doc.status)
                    $('button[data-label="Pay%20Invoice"]').prop('disabled', false);
                    return 0;
                }
                if( !frm.doc.customer_name || !frm.doc.name ){
                    frappe.msgprint('Fill empty invoice values first!');
                    $('button[data-label="Pay%20Invoice"]').prop('disabled', false);
                    return 0;

                }    
                frappe.call({
                    method:"ipconnex_stripe_payment.ipconnex_stripe_payment.payement.processPayment",
                    args:{
                        doctype:frm.doc.doctype ,
                        docname:frm.doc.name
                  
                    },
                    callback: function(res) { 
                      if(res.message.status==1){ 
                        Swal.fire({
                        icon: 'success',
                        title: 'Success',
                        text: res.message.message,
                        });
                  
                      }else{ 
                        Swal.fire({
                        icon: "warning",
                        title: "Warning",
                        text: res.message.message,
                      }); 
                  
                    }
                  }
                });
        });
    }
});
frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        frm.add_custom_button(__('Pay Invoice'), function(event) {
            $('button[data-label="Pay%20Invoice"]').prop('disabled', true);

            if(frm.doc.status !== 'Unpaid' && frm.doc.status !== 'Overdue') {
                frappe.msgprint('This invoice is ' + frm.doc.status)
                $('button[data-label="Pay%20Invoice"]').prop('disabled', false);
                return 0;
            }
            if( !frm.doc.customer_name || !frm.doc.name ){
                frappe.msgprint('Fill empty invoice values first!');
                $('button[data-label="Pay%20Invoice"]').prop('disabled', false);
                return 0;

            }    
            frappe.call({
                method:"ipconnex_stripe_payment.ipconnex_stripe_payment.payement.processPayment",
                args:{
                    doctype:frm.doc.doctype ,
                    docname:frm.doc.name
              
                },
                callback: function(res) { 
                  if(res.message.status==1){ 
                    Swal.fire({
                    icon: 'success',
                    title: 'Success',
                    text: res.message.message,
                    });
              
                  }else{ 
                    Swal.fire({
                    icon: "warning",
                    title: "Warning",
                    text: res.message.message,
                  }); 
              
                }
              }
            });
        })

    }
});

frappe.ui.form.on('Stripe Settings', { 
    onload: function(frm) {
        if (frappe.user.has_role('Administrator'))
            { frm.set_df_property('secret_key', 'hidden', 0); } 
        else 
            { frm.set_df_property('secret_key', 'hidden', 1); } 
    } 
});

frappe.ui.form.on('Payment Method', {
    after_save: function(frm) {
        frm.set_df_property('card_expired', 'hidden', 1);
        frm.set_df_property('card_expire_soon', 'hidden', 1);
        if(frm.doc.expiration){
            let currentDate = new Date();
            let currentMonth = currentDate.getMonth() ;
            let currentYear = currentDate.getFullYear();
            let cardM = parseInt(frm.doc.expiration.substring(0, 2), 10); 
            let cardY = parseInt(frm.doc.expiration.substring(2), 10); 
            if((currentYear%100)>90 || (cardY%100>90)){
                cardY =(cardY+20)%100;
                currentYear =(currentYear+20)%100;
            }else{
                currentYear = currentYear%100;
            }
            let currentCoef=currentYear*12+currentMonth;
            let cardCoef=cardY*12+cardM;
            if (currentCoef >= cardCoef ) {
                // show expired card
                frm.set_df_property('card_expired', 'hidden', 0);

            } else if (currentCoef +3 >= cardCoef ) {
                // show card will expire soon 
                frm.set_df_property('card_expire_soon', 'hidden', 0);
            }
        }
    },
    onload: function(frm) {
        frm.set_df_property('card_expired', 'hidden', 1);
        frm.set_df_property('card_expire_soon', 'hidden', 1);
        if(frm.doc.expiration){
            let currentDate = new Date();
            let currentMonth = currentDate.getMonth() ;
            let currentYear = currentDate.getFullYear();
            let cardM = parseInt(frm.doc.expiration.substring(0, 2), 10); 
            let cardY = parseInt(frm.doc.expiration.substring(2), 10); 
            if((currentYear%100)>90 || (cardY%100>90)){
                cardY =(cardY+20)%100;
                currentYear =(currentYear+20)%100;
            }else{
                currentYear = currentYear%100;
            }
            let currentCoef=currentYear*12+currentMonth;
            let cardCoef=cardY*12+cardM;
            if (currentCoef >= cardCoef ) {
                frm.set_df_property('card_expired', 'hidden', 0);

            } else if (currentCoef +3 >= cardCoef ) {
                frm.set_df_property('card_expire_soon', 'hidden', 0);
            }


        }

    }, 
    refresh: function(frm) {
        
        $('button[data-fieldname = "add"]').click(function(e) {
            $('button[data-fieldname = "add"]').prop('disabled', true);
            try{
                e.stopImmediatePropagation();
            let name = frm.doc.customer ; 
            let number = frm.doc.new_card_number ; 
            let expiration = frm.doc.new_expiration ; 
            let cvc = frm.doc.cvc ; 
            let stripeId = frm.doc.stripe_id ; 
            if(!name || ! number || ! expiration || ! cvc  ){
                let msg=""
                if(!name){
                    msg=msg+"name ";
                }
                if(!number){
                    msg=msg+"Number ";
                }
                if(!expiration){
                    msg=msg+"ExpirationDate ";
                }
                if(!cvc){
                    msg=msg+"CVC ";
                }
                frappe.msgprint('Missing Data : '+msg );
                $('button[data-label="Pay%20Invoice"]').prop('disabled', false);
                return 0;
            }
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Stripe Settings",
                    fields: ["secret_key", "gateway_name","source"], 
                    filters: { /*
                        "field1": "some_value",
                        "field2": ["!=", "other_value"],
                        "field3": ["like", "%search_text%"]*/
                    }
                },
                callback: function(response) {
                    var settings = response.message[0];
                    if(!settings){
                        frappe.msgprint('Stripe settings not found!');
                        $('button[data-fieldname = "add"]').prop('disabled', false);
                        return 0;
                    }
                    var sec_key=settings.secret_key;
                    var source=settings.source;   
                    if(!sec_key || !source){
                        frappe.msgprint('Error while reading Stripe Settings !');
                        $('button[data-fieldname = "add"]').prop('disabled', false);
                        return 0;
        
                    }     
                    frappe.call({
                        method: "ipconnex_stripe_payment.ipconnex_stripe_payment.payement.addPaymentCard",
                        args: {
                            name:name, 
                            number:number, 
                            expiration:expiration, 
                            cvc:cvc, 
                            stripeId:stripeId, 
                            source:source,
                            sec_key:sec_key
                        },
                        callback: function(response) {
                            var data =JSON.parse(response.message);
                            if(data.error==0){ // no errors 
                    
                                // replace old values
                                cur_frm.set_value("stripe_id", data.stripeId);
                                cur_frm.set_value("current_card", data.number);
                                cur_frm.set_value("expiration", data.expiration);
                                
                                // clear new values
                                cur_frm.set_value("new", false);
                                cur_frm.set_value("new_card_number", '');
                                cur_frm.set_value("new_expiration", '');
                                cur_frm.set_value("cvc", '');
                                cur_frm.save();
                            }
                            frappe.msgprint(data.message);
                            $('button[data-fieldname = "add"]').prop('disabled', false);
                        }
                    });

                }
            });
            
        }catch(error){
            return 0;
        }
            
        });
    }
});
