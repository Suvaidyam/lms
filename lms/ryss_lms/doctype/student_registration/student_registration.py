# Copyright (c) 2024, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StudentRegistration(Document):
	# def validate(self):
	# 	if self.docstatus != "2" and not self.user:
	# 		self.user = frappe.session.user

	def on_submit(self):
		pass
		# enroll in a course in which student apply for enrollment

