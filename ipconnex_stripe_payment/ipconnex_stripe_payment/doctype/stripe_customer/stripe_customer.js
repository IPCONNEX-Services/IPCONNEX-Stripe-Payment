var script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@10';
document.head.appendChild(script);

frappe.ui.form.on('Stripe Customer', {
    refresh:function(frm){

        $("button[data-fieldname='get_stripe_id']").off("click").on("click",
            function(){  
                frappe.call({
                    method: "ipconnex_stripe_payment.ipconnex_stripe_payment.payement.getCustomer",
                    args: {email:frm.doc.email, full_name:frm.doc.customer
                    },
                    callback: function(res){ 
                        console.log(res.message.status);
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
                        
                        console.log(res.message.result);
                        /*
                        frm.set_value({"stripe_id":res.message.id}).then(()=>{
                            if(frm.doc.__unsaved){
                                frm.save();
                            }
                            Swal.fire({
                                icon: 'success',
                                title: 'Success',
                                text: res.message.message,
                            });
                        })*/
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
