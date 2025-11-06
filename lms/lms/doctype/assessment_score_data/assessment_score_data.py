# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document

class AssessmentScoreData(Document):
	def after_insert(self):
		user_exists = frappe.db.exists("User", {"name": self.frappe_id}) if self.frappe_id else False
		if user_exists:
			self.apply_user_permissions()
	
	def before_delete(self):
		self.delete_user_permissions()
        
	def before_save(self):
		self._any_fail_found = False
		self.semester_maximum_marks=0
		self.semester_obtaind_marks=0
		self.total_credits=0
		self.no_of_modules_pass=0

		

		self.calculate_fields("own_fields", "own_field__continue_assessment_70", "own_field__end_assessment_30", "own_field__continue_assessment_pf", "own_field__end_assessment_pf")
		self.calculate_fields("lms_fields", "lms__continuous_assessment_70", "lms__end_assessment_30", "lms__continuous_assessment_pf", "lms__end_assessment_pf")
		self.calculate_fields("nf_fields", "nf__continue_assessment_70", "nf__end_assessment_30", "nf__continue_assessment_pf", "nf__end_assessment_pf")
		self.calculate_fields("managing_farms", "managing_farms__continue_assessment_70", "managing_farms__end_assessment_30", "managing_farms__continue_assessment_pf", "managing_farms__end_assessment_pf")
		self.calculate_fields("research_methods", "research_methods__continue_assessment_70", "research_methods__end_assessment_30", "research_methods__continue_assessment_pf", "research_methods__end_assessment_pf")
		self.calculate_fields("food_systems", "food_systems__continue_assessment_70", "food_systems__end_assessment_30", "food_systems__continue_assessment_pf", "food_systems__end_assessment_pf")
		self.calculate_fields("ofe_fields", "ofe__continue_assessment_70", "ofe__end_assessment_30", "ofe__continue_assessment_pf", "ofe__end_assessment_pf")
		self.calculate_fields("or_fields", "or__continue_assessment_70", "or__end_assessment_30", "or__continue_assessment_pf", "or__end_assessment_pf")
		self.calculate_fields("ct_fields", "ct__continue_assessment_70", "ct_end_assessment_30", "ct__continue_assessment_pf", "ct__end_assessment_pf")
		self.calculate_fields("crv_fields", "crv__continue_assessment_70", "crv__end_assessment_30", "crv__continue_assessment_pf", "crv__end_assessment_pf")
		self.calculate_fields("dnf_fields", "dnf__continuous_assessment_70", "dnf__end_assessment_30", "dnf__continuous_assessment_pf", "dnf__end_assessment_pf")


		self.semester_passfail = "Fail" if self._any_fail_found else "Pass"
		self.semester_= round((self.semester_obtaind_marks / self.semester_maximum_marks * 100), 2) if self.semester_maximum_marks else 0
		self.semester_gpa = round((self.semester_ / 10), 2)

	
	
	
		


	def calculate_fields(self, table_name, cont_field, end_field, cont_pf_field, end_pf_field):
		total_credits = 0
		total_weighted = 0
		

		child_table = getattr(self, table_name, [])  # dynamically access the child table
		def safe_float(value):
			try:
				return float(value)
			except (ValueError, TypeError):
				return 0

	
		
		for row in child_table:
			# Safely convert to floats
			continue_assessment = safe_float(getattr(row, cont_field, 0) or 0)
			end_assessment = safe_float(getattr(row, end_field, 0) or 0)
			credits = safe_float(getattr(row, "credits", 0) or 0)

			# Step 1: Calculate total marks
			total = continue_assessment + end_assessment
			row.assessment_total = total

			# Step 2: Weighted totals
			weighted_total = credits * 100
			obtained_weighted = total * credits
			row.weighted_total = weighted_total
			row.obtained_weighted = obtained_weighted

			# Step 3: Percentage
			row.total_percent = (obtained_weighted / weighted_total * 100) if weighted_total else 0

			# Step 4: Pass/Fail logic
			weighted_continue_threshold = 70 * 0.5  # 35
			weighted_end_threshold = 30 * 0.4       # 12
			weighted_total_threshold = 100 * 0.5          # 50

			setattr(row, cont_pf_field, "Pass" if continue_assessment >= weighted_continue_threshold else "Fail")
			setattr(row, end_pf_field, "Pass" if end_assessment >= weighted_end_threshold else "Fail")


			if continue_assessment >= weighted_continue_threshold and end_assessment >= weighted_end_threshold and total >= weighted_total_threshold:
				self.no_of_modules_pass += 1
				row.module_filnal = "Pass"
				
			else:
				row.module_filnal = "Fail"
				self._any_fail_found = True 

			# Accumulate totals
			total_credits += credits
			total_weighted += obtained_weighted
   
   
		
		
		self.total_credits = int(self.total_credits or 0) + int(total_credits or 0)
		self.semester_maximum_marks = int(self.semester_maximum_marks or 0) + int(total_credits or 0) * 100
		self.total_obtained_weighted = total_weighted
		self.semester_obtaind_marks = int(self.semester_obtaind_marks or 0) + int(total_weighted or 0)
  
  
	def apply_user_permissions(self):
		if not frappe.db.exists("User Permission", {"user": self.frappe_id, "allow": self.doctype,}):
			new_doc = frappe.new_doc("User Permission")
			new_doc.user = self.frappe_id
			new_doc.allow = self.doctype
			new_doc.apply_to_all_doctypes = 1
			new_doc.for_value = self.name
			new_doc.insert()
   
	# def delete_user_permissions(self):
	# 	record_count = frappe.db.count("Assessment Score Data", {"frappe_id": self.frappe_id})
	# 	print("Record Count================="*100, record_count)
	# 	# if record_count == 1:
	# 	frappe.db.delete("User Permission", {"user": self.frappe_id, "allow": self.doctype, "for_value": self.name})

	def delete_user_permissions(self):
    # Count how many Assessment Score Data records exist for this frappe_id
		record_count = frappe.db.count("Assessment Score Data", {"frappe_id": self.frappe_id})
		
		# If this is the only one, remove its user permission
		if record_count == 1:
			frappe.db.delete(
				"User Permission",
				{
					"user": self.frappe_id,
					"allow": self.doctype,
					"for_value": self.name
				},
				ignore_permissions=True
			)	
		