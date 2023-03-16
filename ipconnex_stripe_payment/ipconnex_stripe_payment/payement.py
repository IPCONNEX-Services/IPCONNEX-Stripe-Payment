
from __future__ import unicode_literals
import frappe
import json
from six import string_types
from frappe import _
from frappe.utils import flt
import stripe
import random


@frappe.whitelist()
def getPayementData(invoice_name,customer_name):
    data=frappe.get_all("Sales Invoice",filters = {
    'name': invoice_name},
    fields=['name', 'customer','total', 'debit_to','company' ] )
    invoice={}
    if(len(data)>0):
        invoice=data[0]
    data =frappe.get_all("Payment Method",filters = {
    'customer': customer_name},
    fields=['name','customer', 'stripe_id','enabled','fail_count'] )    
    payment_method={}
    if(len(data)>0):
        payment_method=data[0]
    result={}
    for key in invoice: 
        result[key]=invoice[key]
    for key in payment_method: 
        result[key]=payment_method[key]
    return json.dumps(result)

@frappe.whitelist()
def payInvoice(secKey,stripeID,amount):
    stripe.api_key = secKey
    random_number = random.randint(0,4)

    
    result={}
    
    try:
        
        payement = stripe.Charge.create(
            amount= round(float(amount)*100),
            currency="cad",
            customer=stripeID,
            description="Fonotel Invoice")
        
        result["message"]="Payment processed with success"
        result["error"]=0
    except stripe.error.CardError as e:
        # Handle card error
        result["message"]="Error while processing the payment ! Card Error"
        result["error"]=1
    except stripe.error.InvalidRequestError as e:
        # Handle invalid request error
        result["message"]="Error while processing the payment ! Invalid Request"
        result["error"]=1
    except stripe.error.AuthenticationError as e:
        # Handle authentication error
        result["message"]="Error while processing the payment ! Authentication Error"
        result["error"]=1
    except stripe.error.APIConnectionError as e:
        # Handle API connection error
        result["message"]="Error while processing the payment ! Connection Error"
        result["error"]=1
    except stripe.error.StripeError as e:
        # Handle all other Stripe errors
        result["message"]="Error while processing the payment ! Stripe Error "
        result["error"]=1
    """
    if(random_number>1):
        # payment done 
        result["message"]="Payment processed with success"
        result["error"]=0
    
    else:
        # payment done 
        result["message"]="Error while processing the payment"
        result["error"]=1"""
    return json.dumps(result)


@frappe.whitelist()
def updatePaymentMethod(methodName,new_count,new_date=""):
    doc = frappe.get_doc('Payment Method', methodName)
    # Modify the attribute values
    doc.fail_count = new_count
    doc.last_fail_date = new_date
    # Save the changes
    result=doc.save()
    return json.dumps([new_count,new_date])

@frappe.whitelist()
def addPaymentCard(name,number,expiration,cvc,stripeId,source,sec_key):
    result={"name":name,"number":number,"expiration":expiration,
            "cvc":cvc,"stripeId":stripeId,"source":source,"sec_key":sec_key}
    stripe.api_key = sec_key
    
    exp_month = expiration[:2]
    exp_year = int('20' + expiration[-2:])

    if(not stripeId):
        stripeId = stripe.Customer.create(name=name)['id']


    try: 
        pm = stripe.PaymentMethod.create(
            type="card",
            card =  {
                "number": number,
                "exp_month": exp_month,
                "exp_year": exp_year,
                "cvc": cvc,
        })
        stripe.PaymentMethod.attach(
            pm,
            customer= stripeId,
        )
        numberHidden = '************' + number[-4:]
        result={"stripeId": stripeId,            
                "number": numberHidden,
                "expiration": expiration}
        result["message"]="Card added with success"
        result["error"]=0
    except stripe.error.CardError as e:
        result["message"]="Error while adding the card"
        result["error"]=1
        result["full"]=str(e)

    return json.dumps(result)


        