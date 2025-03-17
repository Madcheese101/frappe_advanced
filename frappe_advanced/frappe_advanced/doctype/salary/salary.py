# Copyright (c) 2025, MadCheese and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
from frappe.utils import today

class Salary(Document):
	# def on_update(self):
		# doc_before_save = self.get_doc_before_save().get("employees")
		# frappe.throw(str(doc_before_save[0].as_dict()))
		# changed_value = self.has_value_changed("employees")
		# if changed_value:
		# 	doc_before_save = self.get_doc_before_save().get("employees")
		# 	frappe.throw(str(doc_before_save))


	@frappe.whitelist()
	def transfer_employee(self, selected_emp, new_branch):
		
		progress_title = "جاري نقل الموظف (الرجاء الانتظار)"
		frappe.publish_progress(percent=0, title=progress_title, description='جاري التحضير لنقل الموظف')
		
		new_branch_doc = frappe.get_doc("Salary", {"branch":new_branch})
		# frappe.throw(str(new_branch_doc.manager))
		emp_doc = frappe.get_doc("Employee", selected_emp["emp_id"])
		new_pos_profile = frappe.get_doc("POS Profile", {"branch": new_branch})
		
		if selected_emp["set_permissions"] == 1:
			frappe.publish_progress(percent=0, title=progress_title, description='تعديل نقاط البيع')
			# add employee to new pos profile
			self.set_pos_profile(selected_emp, new_pos_profile)

			frappe.publish_progress(percent=16.66, title=progress_title, description='تعديل بيانات الموظف')
			# change employee branch in employee doctype
			if emp_doc.branch != new_branch:
				emp_doc.branch = new_branch
				emp_doc.reports_to = new_branch_doc.manager
				emp_doc.save(ignore_permissions=True)

			frappe.publish_progress(percent=33.32, title=progress_title, description='تعديل تصريحات الموظف')
			# set user permissions
			self.set_user_permissions(selected_emp, new_pos_profile.name, new_branch, new_pos_profile.warehouse)
		
		frappe.publish_progress(percent=50, title=progress_title, description='اضافة الموظف للفرع الجديد')
		# add employee to new branch (salary doctype)
		self.set_new_salary(selected_emp, new_branch_doc)

		frappe.publish_progress(percent=66, title=progress_title, description='حذف الموظف من الفرع القديم')
		# remove employee from old branch (salary doctype)
		new_employees = [row for row in self.get("employees") if row.get("emp_id") != selected_emp["emp_id"]]
		
		self.set("employees", new_employees)
		self.add_comment("Edit", text=f"تم تحويل الموظف {selected_emp['emp_name']} لفرع {new_branch}")
		self.save(ignore_permissions=True)
		frappe.publish_progress(percent=100, title=progress_title, description='تم تحويل الموظف بنجاح')
		
	def set_pos_profile(self, selected_emp, new_pos_profile):
		pos_users = new_pos_profile.get("applicable_for_users")
		new_pos_profile_name = new_pos_profile.get("name")
		
		# check if employee already exists in new pos profile
		exists_in_new_pos = any(d.get("user") == selected_emp["user_id"] 
			for d in pos_users)
		
		# add employee to new pos profile
		if not exists_in_new_pos:
			other_pos_users= frappe.get_all("POS Profile",
				filters={"name": ["!=", new_pos_profile_name]},
				fields=["applicable_for_users.user as user"],
				pluck= "user")

			if(selected_emp["user_id"] in other_pos_users):
				frappe.db.delete("POS Profile User", {
					"parent": ["!=", new_pos_profile_name],
					"user": selected_emp["user_id"]
				})
			
			new_pos_profile.append("applicable_for_users", {
				"user": selected_emp["user_id"],
				"default": 1
			})
			new_pos_profile.save(ignore_permissions=True)
	
	def set_new_salary(self, selected_emp, new_branch_doc):
		# check if employee already exists in new branch
		exists_in_new_branch = any(d.get("emp_id") == selected_emp["emp_id"] 
			for d in new_branch_doc.get("employees"))
		
		# add employee to new branch (salary doctype)
		if not exists_in_new_branch:
			new_branch_doc.append("employees", {
				"emp_name": selected_emp["emp_name"],
				"emp_id": selected_emp["emp_id"],
				"user_id": selected_emp["user_id"],
				"shift_type": selected_emp["shift_type"],
				"designation": selected_emp["designation"],
				"salary": selected_emp["salary"],
				"set_permissions": selected_emp["set_permissions"]
			})
			from_branch = self.branch if self.branch else self.name
			new_branch_doc.add_comment("Edit", text=f"تم ارسال الموظف {selected_emp['emp_name']} من {from_branch}")
			new_branch_doc.save(ignore_permissions=True)
	
	def set_user_permissions(self, selected_emp, new_pos_profile, new_branch, new_warehouse):
		posProfile_perm = frappe.get_doc("User Permission", {"user":selected_emp["user_id"] , "allow": "POS Profile"})
		posProfile_perm.for_value = new_pos_profile
		posProfile_perm.is_default = 1
		posProfile_perm.save(ignore_permissions=True)

		branch_perm = frappe.get_doc("User Permission", {"user":selected_emp["user_id"] , "allow": "Branch"})
		branch_perm.for_value = new_branch
		branch_perm.is_default = 1
		branch_perm.save(ignore_permissions=True)

		warehouse_perm = frappe.get_doc("User Permission", {"user":selected_emp["user_id"] , "allow": "Warehouse"})
		warehouse_perm.for_value = new_warehouse
		warehouse_perm.is_default = 1
		warehouse_perm.save(ignore_permissions=True)

	@frappe.whitelist()
	def employee_leave(self, selected_emp):
		emp_doc = frappe.get_doc("Employee", selected_emp["emp_id"])
		emp_doc.status = "Left"
		emp_doc.relieving_date = today()
		
		new_employees = [row for row in self.get("employees") if row.get("emp_id") != selected_emp["emp_id"]]
		
		self.set("employees", new_employees)
		self.add_comment("Edit", text=f"مغادرة الموظف {selected_emp['emp_name']}")
		self.save()

		user_doc = frappe.get_doc("User", selected_emp["user_id"])
		user_doc.enabled = 0
		user_doc.save()

	def insert_salary_journal_entry(self, receipt_number, receipt_date):
		employees = self.get("employees")
		total_salaries = sum(row.get("salary") for row in employees)
		user_remarks = "مرتبات الموظفين في  " + self.name + "<br>" + "<ul>"
		# default_cash_account = frappe.db.get_value("Company", company, ["default_cash_account"])

		for employee in employees:
			user_remarks += "<li>" + employee.get("emp_name") + " : " + str(employee.get("salary")) + "</li>"
		user_remarks += "</ul>"

		
		
		# create journal entry
		#######################
		salaries_je = frappe.new_doc('Journal Entry')
		
		salaries_je.voucher_type = "Journal Entry"
		salaries_je.title = f"مرتبات الموظفين  {self.name}"
		salaries_je.cheque_no = f'إذن صرف {receipt_number}'
		salaries_je.cheque_date = receipt_date
		salaries_je.user_remark = user_remarks
		salaries_je.posting_date = today()
		# money to account
		to_ = {"account": "5213 - المرتبات الأساسية - BC",
			"cost_center": self.cost_center,
			"debit_in_account_currency": total_salaries}
		# money from account
		from_ = {"account":"1111 - الخزينة الرئيسية نقدي - BC",
			"cost_center": self.cost_center,
			"credit_in_account_currency": total_salaries}
		
		salaries_je.append("accounts",to_)
		salaries_je.append("accounts",from_)

		salaries_je.save(ignore_permissions=True)
		salaries_je.submit()

@frappe.whitelist()
def insert_salary_journal_entry(receipt_list):
	# salary_branches = frappe.db.get_list("Salary", pluck="name")
	receipt_list = json.loads(receipt_list)
	for receipt in receipt_list:
		branch_doc = frappe.get_doc("Salary", receipt["salary_doc_name"])
		branch_doc.insert_salary_journal_entry(receipt_number=receipt["receipt_no"], receipt_date=receipt["receipt_date"])

def get_branches_salaries():
	branches = frappe.db.get_list("Salary", fields=["name", "salaries_total"])
	msg = "<ul>"
	for branch in branches:
		msg += "<li>" + branch["name"] + " : " + str(branch["salaries_total"]) + "</li>"
	msg += "</ul>"
	return msg