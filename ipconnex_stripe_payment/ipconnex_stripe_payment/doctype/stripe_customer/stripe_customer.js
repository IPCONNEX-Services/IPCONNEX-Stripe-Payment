var script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@10';
document.head.appendChild(script);

frappe.ui.form.on('Stripe Customer', {
    refresh:function(frm){

        $("button[data-fieldname='get_stripe_id']").off("click").on("click",
            function(){  
                frappe.call({
                    method: "ipconnex_stripe_payment.ipconnex_stripe_payment.payement.getCustomer",
                    args: {email:frm.doc.email, full_name:frm.doc.customer,sec_key:"sk_test_51CJ0txGmGCEPYxBaRPZlAeZMOMQySVQANE6E8dgrXsK075nlGu3G1amWhnkAKoG04HoP7qihiqOieGPkyosvj0BN00hRDOTR42"
                    },
                    callback: function(res){ 
                        console.log(res.status);
                        if(res.status==1){ 
                            Swal.fire({
                                icon: 'success',
                                title: 'Success',
                                text: res.message,
                            });
                        }else{ 
                            Swal.fire({
                            icon: "warning",
                            title: "Warning",
                            text: res.message,
                        });

                        }
                    
                    
                    
                    }});
        } );
    }
});
