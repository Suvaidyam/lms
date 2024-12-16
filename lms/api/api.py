@frappe.whitelist()
def get_states_by_country(country):
    return frappe.get_all('State', filters={'country': country}, fields=['name'])

@frappe.whitelist()
def get_districts_by_state(state):
    return frappe.get_all('District', filters={'state': state}, fields=['name'])
