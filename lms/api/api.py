<<<<<<< HEAD
@frappe.whitelist()
def get_states_by_country(country):
    return frappe.get_all('State', filters={'country': country}, fields=['name'])

@frappe.whitelist()
def get_districts_by_state(state):
    return frappe.get_all('District', filters={'state': state}, fields=['name'])
=======
import frappe
@frappe.whitelist()
def get_lms_courses():
    return frappe.get_list(
        'LMS Course',
        fields=['title', 'image','duration__month',"term_start_date"],
        # filters={'status': "Approved"},
        order_by='creation desc'
    )
    
@frappe.whitelist()
def get_lms_batches():
    return frappe.get_list(
        'LMS Batch',
        fields=['meta_image', 'title','seat_count','batch_details', 'start_date', 'end_date', 'start_time', 'end_time',],
        order_by='creation desc'
    )
>>>>>>> dev_bittuk
