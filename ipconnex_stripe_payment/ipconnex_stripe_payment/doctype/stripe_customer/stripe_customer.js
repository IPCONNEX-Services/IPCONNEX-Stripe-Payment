var script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@10';
document.head.appendChild(script);

function copyTextToClipboard(text) {
    var textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
}
  
frappe.ui.form.on('Stripe Customer', {
    customer:function(frm){ 
        if(frm.doc.customer && frm.doc.name.startsWith("new-stripe-customer")){
            frappe.call({
                method: "ipconnex_stripe_payment.ipconnex_stripe_payment.payement.getEmail",
                args: {customer:frm.doc.customer
                },
                callback: function(res){ 
                    if(res.message.status){
                        frm.set_value({"email":res.message.result});

                    }
                }
            });



        }
    },
    refresh:function(frm){
        $("button[data-fieldname='get_stripe_id']").off("click").on("click",
            function(){  
                frappe.call({
                    method: "ipconnex_stripe_payment.ipconnex_stripe_payment.payement.getCustomer",
                    args: {email:frm.doc.email, full_name:frm.doc.customer
                    },
                    callback: function(res){ 
                        if(res.message.status==1){ 
                            frm.set_value({"stripe_id":res.message.id}).then(()=>{
                                if(frm.doc.__unsaved){
                                    frm.save();
                                }
                                Swal.fire({
                                    icon: 'success',
                                    title: 'Success',
                                    text: res.message.message,
                                });
                            })
                        }else{ 
                            Swal.fire({
                            icon: "warning",
                            title: "Warning",
                            text: res.message.message,
                        });
                        }
                    }});
        } ); 
        $("button[data-fieldname='check_cards']").off("click").on("click",
            function(){  
                frappe.call({
                    method: "ipconnex_stripe_payment.ipconnex_stripe_payment.payement.getCustomerCards",
                    args: {customer_id:frm.doc.stripe_id
                    },
                    callback: function(res){ 
                        if(res.message.status==1){ 
                            frm.set_value({"cards_list":res.message.result}).then(()=>{
                                if(frm.doc.__unsaved){
                                    frm.save();
                                }
                                Swal.fire({
                                    icon: 'success',
                                    title: 'Success',
                                    text: res.message.message,
                                });
                            })
                        }else{ 
                            Swal.fire({
                            icon: "warning",
                            title: "Warning",
                            text: res.message.message,
                        });
                        }
            }});
        } );
        $("button[data-fieldname='get_new_card_token']").off("click").on("click",
            function(){  
                frappe.call({
                    method: "ipconnex_stripe_payment.ipconnex_stripe_payment.payement.getNewCardToken",
                    args: {customer_id:frm.doc.stripe_id
                    },
                    callback: function(res){ 
                        if(res.message.status==1){ 
                            frm.set_value({"card_token":res.message.result}).then(()=>{
                                if(frm.doc.__unsaved){
                                    frm.save();
                                }
                                new_card_url=window.location.href.split("/app")[0]+"add_card?token="+res.message.result
                                try{
                                    copyTextToClipboard(new_card_url);                                            
                                    Swal.fire({
                                        icon: 'success',
                                        title: 'Success',
                                        html: res.message.message+"<br>"+"New Card Link Copied To Clipboard"
                                    });
                                }catch(e){
                                    Swal.fire({
                                        icon: 'success',
                                        title: 'Success',
                                        text: res.message.message,
                                    });
                                }
                            })
                        }else{ 
                            Swal.fire({
                            icon: "warning",
                            title: "Warning",
                            text: res.message.message,
                        });
                        }
                    }});
        } );
    }
});
