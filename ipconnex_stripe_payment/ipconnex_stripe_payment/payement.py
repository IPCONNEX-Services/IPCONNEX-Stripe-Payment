
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

@frappe.whitelist() 
def generateClientSecret(amount,currency,methods):
    currency='cad'
    methods=['card']
    try:
        
        stripe_settings=frappe.db.get_all("Stripe Settings",
                fields=["publishable_key","secret_key"],order_by='modified', limit_page_length=0)
        if(len(stripe_settings)==0):
            return{
                "error":'Set Stripe Settings first !',
                "status":0
            }
        stripe.api_key=stripe_settings[0].secret_key
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,  
            currency=currency,
            payment_method_types=methods
        )
        return {
            "client_secret":payment_intent.client_secret,
            "status":1
        }
    except stripe.error.StripeError as e:
        return {
            "error":str(e),
            "status":0
        }
    
@frappe.whitelist() 
def checkPaymentStatus(client_secret):
    try:
        # Retrieve the payment intent
        payment_intent = stripe.PaymentIntent.retrieve(client_secret.split("_secret_")[0])

        # Check the status of the payment intent
        print(f"PaymentIntent status: {payment_intent.status}")

        # Based on the status, you can take further actions
        if payment_intent.status == "succeeded":
            # TODO create payment entry if not existing ...
            return {
                "title":"Success",
                "message":"payment has been successfully processed.",
                "status":1
            }
        elif payment_intent.status == "requires_payment_method":
            return {
                "title":"Info",
                "message":"Waiting for your payment ",
                "status":1
            }
        else:
            return {
                "title":"Error",
                "message":"Transaction failed ! server error ",
                "status":1
            }

    except stripe.error.StripeError as e:
        return {
            "error":str(e),
            "status":0
        }

@frappe.whitelist() 
def getCustomer(email, full_name):
    try:        
        stripe_settings=frappe.db.get_all("Stripe Settings",fields=["secret_key"],order_by='modified', limit_page_length=0)
        if(len(stripe_settings)==0):
            return {"message":"Please configure Stripe Settings first","status":0}
        stripe.api_key = stripe_settings[0]["secret_key"]
        customers = stripe.Customer.list(email=email).auto_paging_iter()
        for customer in customers:
            if customer.name == full_name:
                # Customer found, return existing ID
                return {"id":customer.id,"message":"The Stripe Customer already exists ","status":1}
        new_customer = stripe.Customer.create(email=email, name=full_name)
        return  {"id":new_customer.id,"message":"A New Stripe Customer Created","status":1}
    except Exception as e :
        return  {"message":str(e),"status":0}
    
@frappe.whitelist() 
def getCustomerCards(customer_id):
    try:
        stripe_settings=frappe.db.get_all("Stripe Settings",fields=["secret_key"],order_by='modified', limit_page_length=0)
        if(len(stripe_settings)==0):
            return {"message":"Please configure Stripe Settings first","status":0}
        stripe.api_key = stripe_settings[0]["secret_key"]
        payment_methods = stripe.PaymentMethod.list(
            customer=customer_id,
            type="card"  
        )
        card_details = []
        for pm in payment_methods.data:
            card_info = {
                "brand": pm.card.brand,  
                "last_digits": pm.card.last4,  
                "exp_date": str(pm.card.exp_month) +"/"+str(pm.card.exp_year),
                "card_id": pm.id  
            }
            card_details.append(card_info)
        return {"result":card_details,"status":1,"message":"Cards Updated !"}
    except Exception as e :
        return {"message":str(e),"status":0}

    
@frappe.whitelist() 
def processPayment(customer_id, payment_method_id, amount,description, currency="usd"):
    try:
        stripe_settings=frappe.db.get_all("Stripe Settings",fields=["secret_key"],order_by='modified', limit_page_length=0)
        if(len(stripe_settings)==0):
            return {"message":"Please configure Stripe Settings first","status":0}
        stripe.api_key = stripe_settings[0]["secret_key"]
        payment_intent = stripe.PaymentIntent.create(
            customer=customer_id,  
            payment_method=payment_method_id, 
            amount=amount,  
            currency=currency,  
            description=description,
            confirm=True,  
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never"
            }
        )
        #Create Payment Entry in frappe 
        return {"result":payment_intent,"status":1}
    except Exception as e :
        return {"message":str(e),"status":0}
    
@frappe.whitelist()
def getNewCardToken(customer_id):
    try:        
        stripe_settings=frappe.db.get_all("Stripe Settings",fields=["secret_key"],order_by='modified', limit_page_length=0)
        if(len(stripe_settings)==0):
            return {"message":"Please configure Stripe Settings first","status":0}
        stripe.api_key = stripe_settings[0]["secret_key"]
        setup_intent = stripe.SetupIntent.create(
            customer=customer_id,
            payment_method_types=['card']
        )
        return {"result":setup_intent.client_secret,"status":1,"message":"Cards Token Updated !"}
    except stripe.error.StripeError as e:
        return {"message":str(e),"status":0}


@frappe.whitelist()
def getEmail(customer):
    try:    
        contacts_name = frappe.db.get_all("Dynamic Link",fields=["parent"],filters={"link_doctype": "Customer","link_name": customer,
                "parenttype": "Contact"},
                order_by='modified', limit_page_length=0)
        emails=[]
        for contact in contacts_name:
            email_doc=frappe.get_doc("Contact", contact.parent)
            email=email_doc.email_id
            if email not in emails and email_doc.is_primary_contact  == 1  : 
                emails.append(email)
        return {"result":",".join(emails),"status":1}
    except stripe.error.StripeError as e:
        return {"message":str(e),"status":0}
    

@frappe.whitelist(allow_guest=True)
def updateCards(client_token):
    try:
        stripe_settings=frappe.db.get_all("Stripe Settings",fields=["secret_key"],order_by='modified', limit_page_length=0)
        if(len(stripe_settings)==0):
            return {"message":"Please configure Stripe Settings first","status":0}
        stripe.api_key = stripe_settings[0]["secret_key"]
        stripe_customers=frappe.db.get_all("Stripe Customer",
                    filters={"card_token":client_token },
                    fields=["name","email","card_token","stripe_id"],order_by='modified', limit_page_length=0)
        if(len(stripe_customers)==0): 
            return {"message":"Customer Card token unfound","status":0}

        payment_methods = stripe.PaymentMethod.list(
            customer=stripe_customers[0].stripe_id,
            type="card"  
        )
        card_details = []
        stripe_customer=frappe.get_doc("Stripe Customer",stripe_customers[0].name)
        
        for child in stripe_customer.cards_list:
                stripe_customer.remove(child)
        stripe_customer.save()
        for pm in payment_methods.data:
            card_info = {
                "brand": pm.card.brand,  
                "last_digits": pm.card.last4,  
                "exp_date": str(pm.card.exp_month) +"/"+str(pm.card.exp_year),
                "card_id": pm.id  
            }
            card_details.append(card_info)
        return {"status":1,"message":"Cards Updated !"}
    except Exception as e :
        return {"message":str(e),"status":0}



