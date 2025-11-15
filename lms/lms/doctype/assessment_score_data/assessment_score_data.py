# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document

class AssessmentScoreData(Document):
  
	def before_save(self):
		self._any_fail_found = False
		self.semester_maximum_marks=0
		self.semester_obtaind_marks=0
		self.total_credits=0
		self.no_of_modules_pass=0
		self.calculate_fun()
		self.semester_passfail = "Fail" if self._any_fail_found else "Pass"
		self.semester_= round((self.semester_obtaind_marks / self.semester_maximum_marks * 100), 2) if self.semester_maximum_marks else 0
		self.semester_gpa = round((self.semester_ / 10), 2)
   
	
	def calculate_fun(self):
		total_credits = 0
		total_weighted = 0
		

		# child_table = getattr(self, table_name, [])  # dynamically access the child table
		def safe_float(value):
			try:
				return float(value)
			except (ValueError, TypeError):
				return 0

	
		
		for row in self.scorecard:
			# Safely convert to floats
			continue_assessment = safe_float(getattr(row, "continuous_assessment", 0) or 0)
			end_assessment = safe_float(getattr(row, "end_assessment", 0) or 0)
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

			setattr(row, 'continuous_assessment_result', "Pass" if continue_assessment >= weighted_continue_threshold else "Fail")
			setattr(row, 'end_assessment_result', "Pass" if end_assessment >= weighted_end_threshold else "Fail")


			if continue_assessment >= weighted_continue_threshold and end_assessment >= weighted_end_threshold and total >= weighted_total_threshold:
				# self.no_of_modules_pass += 1
				self.no_of_modules_pass = (self.no_of_modules_pass or 0) + 1
				row.module_final = "Pass"
				
			else:
				row.module_final = "Fail"
				self._any_fail_found = True 

			# Accumulate totals
			total_credits += credits
			total_weighted += obtained_weighted
   
   
		
		
		self.total_credits = int(self.total_credits or 0) + int(total_credits or 0)
		self.semester_maximum_marks = int(self.semester_maximum_marks or 0) + int(total_credits or 0) * 100
		self.total_obtained_weighted = total_weighted
		self.semester_obtaind_marks = int(self.semester_obtaind_marks or 0) + int(total_weighted or 0)

	