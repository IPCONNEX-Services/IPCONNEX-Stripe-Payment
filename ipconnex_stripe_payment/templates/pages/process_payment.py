import frappe


def get_context(context):
    context.custom_context_variable = "Hello, World!"    
    # Accessing the URL parameter "param"
    param_value = frappe.form_dict.get('param', 'default_value')
    # You can then add this to the context passed to the Jinja template
    context.param_value = param_value