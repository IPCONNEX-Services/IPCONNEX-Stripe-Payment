
from __future__ import unicode_literals
import frappe
import json
from six import string_types
from frappe import _
from frappe.utils import flt
import stripe
import random

def setup_install():
    try:
        email_templates= frappe.get_all(
                             "Email Template",
                            filters={"name": "Stripe Notification IPCONNEX Default template" },
                            fields=["name"])
        if(len(email_templates)==0):
            email_template_doc= frappe.get_doc(
                {   "doctype": "Email Template",
                    "__newname": "Stripe Notification IPCONNEX Default template",
                    "subject": "Stripe Payment Notification - Notification de Payment via Stripe",
                    "use_html": 0,
                    "response": "<div class=\"ql-editor read-mode\"><h1>Stripe Payment Notification - Notification de Payment via Stripe</h1><h3><br></h3><p><span style=\"color: rgb(0, 0, 0);\">Dear </span>{{ customer }}</p><p><br></p><p>We are pleased to inform you that your payment for<span style=\"color: rgb(0, 0, 0);\"> </span><strong style=\"color: rgb(0, 0, 0);\"> {{ doctype }} : # {{ name }}</strong><span style=\"color: rgb(0, 0, 0);\"> &nbsp;</span> has been successfully processed <span style=\"color: rgb(0, 0, 0);\">!</span></p><p><br></p><p><span style=\"color: rgb(0, 0, 0);\">The paid amount using stripe is :&nbsp;</span><strong style=\"color: rgb(0, 0, 0);\">$ {{ amount }} &nbsp;</strong>for a total amount of : <span style=\"color: rgb(0, 0, 0);\">&nbsp;</span><strong style=\"color: rgb(0, 0, 0);\">$ {{ grand_total }} </strong></p><p><br></p><p>Payment Reference on Stripe : <strong style=\"color: rgb(0, 0, 0);\">{{ stripe_payment_ref }} </strong></p><p><span style=\"color: rgb(0, 0, 0);\">﻿Last Card Digits : </span><strong style=\"color: rgb(0, 0, 0);\"> {{ card_last_digits }} </strong></p><p><span style=\"color: rgb(0, 0, 0);\">Expiration Date : </span><strong style=\"color: rgb(0, 0, 0);\">{{ exp_card }} </strong></p><p><br></p><p>If you have any questions or need further assistance, <span style=\"color: rgb(0, 0, 0);\">free to contact us for more information.</span></p><p><br></p><p><span style=\"color: rgb(0, 0, 0);\">Kind Regards,</span></p><p>_________________________________________________________________</p><p><br></p><p>Cher {{ customer }},</p><p><br></p><p>Nous sommes heureux de vous informer que votre paiement pour <strong style=\"color: rgb(0, 0, 0);\">{{ doctype }} : # {{ name }}</strong><span style=\"color: rgb(0, 0, 0);\"> </span>a été traité avec succès !</p><p><br></p><p>Le montant payé via Stripe est de :<span style=\"color: rgb(0, 0, 0);\">&nbsp;</span><strong style=\"color: rgb(0, 0, 0);\">$ {{ amount }}</strong> pour un montant total de : <span style=\"color: rgb(0, 0, 0);\">&nbsp;</span><strong style=\"color: rgb(0, 0, 0);\">$ {{ grand_total }} </strong></p><p><br></p><p>Référence de paiement sur Stripe : <strong style=\"color: rgb(0, 0, 0);\">{{ stripe_payment_ref }} </strong></p><p>Derniers chiffres de la carte : <strong style=\"color: rgb(0, 0, 0);\">{{ card_last_digits }} </strong></p><p> Date d'expiration : <span style=\"color: rgb(0, 0, 0);\"> </span><strong style=\"color: rgb(0, 0, 0);\">{{ exp_card }} </strong></p><p><br></p><p>Si vous avez des questions ou avez besoin de plus d'assistance, n'hésitez pas à nous contacter pour plus d'informations.</p><p><br></p><p>Cordialement,</p></div>",
                 })
            email_template_doc.save(ignore_permissions=True)
    except:
        """fail to create template"""   

    # Add Auto Process Field to sales Invoice
    doctype = "Sales Invoice"
    field_name = "process_on_submit"
    field_type="Check"
    meta=frappe.get_meta(doctype)
    existing_fields=[field.fieldname for field in frappe.get_meta(doctype).fields ]

    if field_name not in existing_fields and False:
        field_doc=frappe.get_doc({
                'parent': doctype, 
                'parentfield': 'fields', 
                'parenttype': 'DocType', 
                'fieldname': field_name, 
                'label': 'Process On Submit', 
                'fieldtype': field_type,  
                'doctype': 'DocField'
        })
        field_doc.insert(ignore_permissions = True)


    # Create link
    links_list=frappe.get_all(
                                "DocType Link",
                                filters={"link_doctype": "Stripe Customer","parent":"Customer" },
                                fields=["name"])
    if( len(links_list)==0):
        link_doc=frappe.get_doc({
            "parent":"Customer",
            "parentfield":"links",
            "parenttype":"Doctype",
            "idx":1,
            "link_doctype":"Stripe Customer",
            "link_fieldname":"customer",
            "group":"Payments",
            "doctype":"DocType Link"
        })
        link_doc.insert(ignore_permissions = True)
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
        payment_intent = stripe.PaymentIntent.retrieve(client_secret.split("_secret_")[0])
        print(f"PaymentIntent status: {payment_intent.status}")

        if payment_intent.status == "succeeded":
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
def processPayment(doctype,docname):
    try:
        stripe_settings=frappe.db.get_all("Stripe Settings",fields=["secret_key","pay_to","email_template","email_sending_account"],order_by='modified', limit_page_length=0)
        if(len(stripe_settings)==0):
            return {"message":"Please configure Stripe Settings first","status":0}
        stripe.api_key = stripe_settings[0]["secret_key"]
        pay_to = stripe_settings[0]["pay_to"]
        sender=stripe_settings[0]["email_sending_account"]
        email_template=stripe_settings[0]["email_template"]
        invoice_doc=frappe.get_doc(doctype,docname)
        stripe_customers= frappe.get_all(
            "Stripe Customer",
            filters={"customer":invoice_doc.customer},
            fields=["name"])
    
        if(len(stripe_customers)!=0 and len(invoice_doc.customer)!=0 )    :
            stripe_customer=frappe.get_doc("Stripe Customer",stripe_customers[0].name)
            customer_id=stripe_customer.stripe_id
            if( len(stripe_customer.cards_list)==0):
                return {"message":"No cards found ! please add a payment method to the current customer","status":0}
            dateStr = frappe.utils.nowdate() 
            for stripe_card in stripe_customer.cards_list:
                try:
                    payment_method_id=stripe_card.card_id
                    if(invoice_doc.disable_rounded_total):
                        amount=min(invoice_doc.outstanding_amount,invoice_doc.grand_total)
                    else:
                        amount=invoice_doc.outstanding_amount
                    amount_cent=int(amount*100)
                    payment_intent = stripe.PaymentIntent.create(
                        customer=customer_id,  
                        payment_method=payment_method_id, 
                        amount=amount_cent,  
                        currency=invoice_doc.currency.lower(),  
                        description=doctype+"#"+docname,
                        confirm=True,  
                        automatic_payment_methods={
                            "enabled": True,
                            "allow_redirects": "never"
                        }
                    )
                    result= {"message":"Invoice Payed using Stripe #"+payment_intent.id,"status":1}
                    payment_entry = frappe.get_doc({
                        "doctype": "Payment Entry",
                        'party_type': 'Customer',
                        'party': invoice_doc.customer,
                        'paid_amount': amount,
                        'received_amount': amount,
                        'target_exchange_rate': 1.0,
                        "paid_from": invoice_doc.debit_to,
                        'paid_to_account_currency': invoice_doc.currency,
                        "paid_from_account_currency": invoice_doc.currency,
                        'paid_to': pay_to,
                        "reference_no": "**** "+stripe_card.last_digits+"/stripe:"+payment_intent.id,
                        "reference_date": dateStr,
                        'company': invoice_doc.company,
                        'mode_of_payment': 'Credit Card',
                        "status": "Submitted",
                        "docstatus": 1,
                        "references": [
                            {
                                "reference_doctype": invoice_doc.doctype,
                                "reference_name": invoice_doc.name,
                                "total_amount": invoice_doc.grand_total,
                                "allocated_amount":amount,
                                "exchange_rate": 1.0,
                                "exchange_gain_loss": 0.0,
                                "parentfield": "references",
                                "parenttype": "Payment Entry",
                                "doctype": "Payment Entry Reference",
                            },
                        ],
                    })
                    payment_entry.save(ignore_permissions=True)  
                    if(email_template and sender ):
                        email_sender= frappe.db.get_value('Email Account', sender ,'email_id')
                        template_doc=frappe.get_doc("Email Template",email_template)
                        mail_template=template_doc.response
                        mail_subject=template_doc.subject
                        context={"amount":amount,
                                 "customer":invoice_doc.customer,
                                 "customer_name":invoice_doc.customer_name,
                                 "grand_total":invoice_doc.grand_total,
                                 "doctype":invoice_doc.doctype,
                                 "name":invoice_doc.name,
                                 "card_last_digits":stripe_card.last_digits,
                                 "stripe_payment_ref":payment_intent.id,
                                 "exp_card":stripe_card.last_digits
                                 }
                        mail_content =frappe.render_template(mail_template,context=context )
                        mail_subject =frappe.render_template(mail_subject,context=context )
                        frappe.sendmail(
                                recipients=stripe_customer.email,
                                sender=email_sender,
                                subject=mail_subject,
                                content=mail_content,     
                                doctype=invoice_doc.doctype,
                                name=invoice_doc.name,
                                read_receipt= "0",
                                print_letterhead= "1",
                                now=True
                                #now=True
                        )
                        frappe.get_doc({
                            "doctype": "Communication",
                            "communication_type": "Communication",
                            "content": mail_content,
                            "subject": mail_subject,
                            "sent_or_received": "Sent",
                            "recipients": stripe_customer.email,
                            "sender": email_sender,
                            "reference_doctype": invoice_doc.doctype,
                            "reference_name": invoice_doc.name,
                        }).insert(ignore_permissions=True)
                    frappe.db.commit()   
                    return result
                except: 
                    payment_method_id=""
            return {"message":"Failed to process payment please check customer cards ","status":0}
        else :
            return {"message":"No Customer Found  ! please link the current Invoice's Customer to Stripe ","status":0}
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
        
        stripe_customer.save()
        for pm in payment_methods.data:
            card_info = {
                "brand": pm.card.brand,  
                "last_digits": pm.card.last4,  
                "exp_date": str(pm.card.exp_month) +"/"+str(pm.card.exp_year),
                "card_id": pm.id  
            }
            card_details.append(card_info)
        stripe_customer.set("cards_list", card_details) 
        stripe_customer.card_token=""
        stripe_customer.save(ignore_permissions=True)
        return {"status":1,"message":"Cards Updated !"}
    except Exception as e :
        return {"message":"Please contact the website Administrator"+str(e),"status":0}

def checkProcessInvoice(doc, method):
    try:
        stripe_settings=frappe.db.get_all("Stripe Settings",fields=["secret_key","pay_to","email_template","email_sending_account"],order_by='modified', limit_page_length=0)
        if(len(stripe_settings)==0):
            frappe.msgprint("Error : Please configure Stripe Settings first")
            return
        stripe.api_key = stripe_settings[0]["secret_key"]
        pay_to = stripe_settings[0]["pay_to"]
        sender=stripe_settings[0]["email_sending_account"]
        email_template=stripe_settings[0]["email_template"]
        stripe_customers= frappe.db.get_all("Stripe Customer",fields=["name","auto_process"],filters={"customer":doc.customer},order_by='modified', limit_page_length=0)
        
        if( (len(stripe_customers)!=0 and len(doc.customer)!=0 ) and ( stripe_customers[0].auto_process )  )   :
            stripe_customer=frappe.get_doc("Stripe Customer",stripe_customers[0].name)
            customer_id=stripe_customer.stripe_id
            if( len(stripe_customer.cards_list)==0):
                frappe.msgprint("Error : No cards found ! please add a payment method to the current customer")
                return
            dateStr = frappe.utils.nowdate() 
            for stripe_card in stripe_customer.cards_list:
                try:
                    payment_method_id=stripe_card.card_id
                    if(doc.disable_rounded_total):
                        amount=min(doc.outstanding_amount,doc.grand_total)
                    else:
                        amount=doc.outstanding_amount
                    amount_cent=int(amount*100)
                    payment_intent = stripe.PaymentIntent.create(
                        customer=customer_id,  
                        payment_method=payment_method_id, 
                        amount=amount_cent,  
                        currency=doc.currency.lower(),  
                        description=doc.doctype+"#"+doc.name,
                        confirm=True,  
                        automatic_payment_methods={
                            "enabled": True,
                            "allow_redirects": "never"
                        }
                    )
                    payment_entry = frappe.get_doc({
                        "doctype": "Payment Entry",
                        'party_type': 'Customer',
                        'party': doc.customer,
                        'paid_amount': amount,
                        'received_amount': amount,
                        'target_exchange_rate': 1.0,
                        "paid_from": doc.debit_to,
                        'paid_to_account_currency': doc.currency,
                        "paid_from_account_currency": doc.currency,
                        'paid_to': pay_to,
                        "reference_no": "**** "+stripe_card.last_digits+"/stripe:"+payment_intent.id,
                        "reference_date": dateStr,
                        'company': doc.company,
                        'mode_of_payment': 'Credit Card',
                        "status": "Submitted",
                        "docstatus": 1,
                        "references": [
                            {
                                "reference_doctype": doc.doctype,
                                "reference_name": doc.name,
                                "total_amount": doc.grand_total,
                                "allocated_amount":amount,
                                "exchange_rate": 1.0,
                                "exchange_gain_loss": 0.0,
                                "parentfield": "references",
                                "parenttype": "Payment Entry",
                                "doctype": "Payment Entry Reference",
                            },
                        ],
                    })
                    payment_entry.save(ignore_permissions=True) 
                    if(email_template and sender ):
                        email_sender= frappe.db.get_value('Email Account', sender ,'email_id')
                        template_doc=frappe.get_doc("Email Template",email_template)
                        mail_template=template_doc.response
                        mail_subject=template_doc.subject
                        context={"amount":amount,
                                 "customer":doc.customer,
                                 "customer_name":doc.customer_name,
                                 "grand_total":doc.grand_total,
                                 "doctype":doc.doctype,
                                 "name":doc.name,
                                 "card_last_digits":stripe_card.last_digits,
                                 "stripe_payment_ref":payment_intent.id,
                                 "exp_card":stripe_card.last_digits
                                 }
                        mail_content =frappe.render_template(mail_template,context=context )
                        mail_subject =frappe.render_template(mail_subject,context=context )
                        frappe.sendmail(
                                recipients=stripe_customer.email,
                                sender=email_sender,
                                subject=mail_subject,
                                content=mail_content,     
                                doctype=doc.doctype,
                                name=doc.name,
                                read_receipt= "0",
                                print_letterhead= "1",
                                now=True
                                #now=True
                        )
                        frappe.get_doc({
                            "doctype": "Communication",
                            "communication_type": "Communication",
                            "content": mail_content,
                            "subject": mail_subject,
                            "sent_or_received": "Sent",
                            "recipients": stripe_customer.email,
                            "sender": email_sender,
                            "reference_doctype": doc.doctype,
                            "reference_name": doc.name,
                        }).insert(ignore_permissions=True)
                    frappe.db.commit()    
                    frappe.msgprint("Success :Invoice Payed using Stripe #"+payment_intent.id)
                    return
                except: 
                    payment_method_id=""
            frappe.msgprint("Error : Failed to process payment please check customer cards ")
            return
            
    except Exception as e :
        frappe.msgprint("Error : "+str(e))




