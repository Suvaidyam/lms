import frappe

def list_query(user):
    if not user:
        user = frappe.session.user
    if "Temp Student" in frappe.get_roles(user) and ("Administrator" not in frappe.get_roles(user)):
        return """(`tabStudent Registration`.owner = '{0}')""".format(user)
    elif ("Administrator" in frappe.get_roles(user)):
        return """(`tabStudent Registration`.workflow_state != 'Draft')"""
    else:
        return ""