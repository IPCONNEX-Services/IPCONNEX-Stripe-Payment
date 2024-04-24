import frappe

no_cache = 1

def get_context(context):
    frappe.clear_cache()
    frappe.cache().flushall()
    context.no_cache = 1
    stripe_settings=frappe.db.get_all("Stripe Settings",
            fields=["publishable_key"],order_by='modified', limit_page_length=0)
    if(len(stripe_settings)!=0):
        context.public_stripe =stripe_settings[0].publishable_key
    payment_token  = frappe.form_dict["token"]
    context.payment_token = payment_token 
    stripe_requests=frappe.db.get_all("Stripe Request",
                    filters={"payment_url": "/process_payment?token="+payment_token },
                    fields=["request_type","customer","sales_invoice","sales_order","requested_amount","currency"],order_by='modified', limit_page_length=0)
    if(len(stripe_requests)!=0):
        context.request_type=stripe_requests[0].request_type
        context.customer=stripe_requests[0].customer
        context.sales_invoice=stripe_requests[0].sales_invoice
        context.sales_order=stripe_requests[0].sales_order
        context.requested_amount=stripe_requests[0].requested_amount
        context.currency=stripe_requests[0].currency
    context.no_cache = 1

