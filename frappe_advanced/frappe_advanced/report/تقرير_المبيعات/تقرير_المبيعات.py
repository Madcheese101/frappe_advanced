# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
import frappe
from frappe import _, _dict

def execute(filters=None):
	data = []
	columns = get_columns(filters)
	data = get_data(filters)
	# frappe.throw(data)
	return columns, data

def get_data(report_filters):
	filters = {}
	data = []
	if report_filters.pos_profile:
		filters["name"] = report_filters.pos_profile

	pos_profiles = frappe.get_list('POS Profile', filters=filters, pluck='name')
	
	profiles_total = 0
	for pos_profile in pos_profiles:
		payments, pos_total = get_payments(report_filters,pos_profile)
		profiles_total += pos_total
		data.append({
			"name": pos_profile,
			"total_amount": pos_total,
			"indent":0,
			"has_value":1})

		if report_filters.group_user or report_filters.detailed:
			for payment in payments:
				data.append(payment)
				if report_filters.group_user:
					users_data = get_employee_data(report_filters, payment.name)
					data.extend(users_data)
				if report_filters.detailed:
					detailed_data = get_detailed_data(report_filters, payment.name)
					data.extend(detailed_data)
		else:
			data.extend(payments)
	data.append({})
	data.append({})
	data.append({"name":"إجمالي نقاط البيع", "total_amount":profiles_total})

	return data
		
def get_payments(filters ,pos_profile):
	fields = [
		   'mode_of_payment as name',
		   'SUM(amount) as total_amount']
	
	if filters.detailed or filters.group_user:
		fields.append("(1) as indent")
		fields.append("(1) as has_value")
	else:
		fields.append("(1) as indent")
		fields.append("(0) as has_value")

	payment_modes = frappe.get_all('POS Payment Method', 
								filters={'parent': pos_profile},
								fields=["mode_of_payment"],
								order_by="mode_of_payment",
								pluck="mode_of_payment")
	result = frappe.get_all("Sales Invoice Payment",
				fields=fields,
				filters={
					"mode_of_payment": ["in", payment_modes],
					"modified":["between",[filters.from_date, filters.to_date]],
					"docstatus":1},
				group_by="mode_of_payment",
				order_by="mode_of_payment")
	get_pos_total = frappe.get_all("Sales Invoice Payment",
				fields=["SUM(amount) as total_amount"],
				filters={
					"mode_of_payment": ["in", payment_modes],
					"modified":["between",[filters.from_date, filters.to_date]],
					"docstatus":1},
				group_by="parentfield",
				pluck="total_amount")
	
	pos_total = 0
	if get_pos_total:
		pos_total = get_pos_total[0]

	return result, pos_total

def get_detailed_data(filters, payment_mode):
	filters["mode_of_payment"] = payment_mode

	data = frappe.db.sql("""
	SELECT
		sp.modified as date,
		sp.parent as invoice,
		(e.employee_name) as employee,
		sp.amount as total_amount,
		(2) as indent,
		(0) as has_value
	FROM
		`tabSales Invoice Payment` sp, `tabEmployee` e
	WHERE
		e.user_id = sp.owner
		AND sp.mode_of_payment = %(mode_of_payment)s
		AND sp.modified BETWEEN %(from_date)s AND %(to_date)s
		AND sp.docstatus = 1
	ORDER BY
		date DESC""",
		filters,
		as_dict=1)
	return data

def get_employee_data(filters, payment_mode):
	filters["mode_of_payment"] = payment_mode

	data = frappe.db.sql("""
	SELECT
		(e.employee_name) as name,
		sum(sp.amount) as total_amount,
		(2) as indent,
		(0) as has_value
	FROM
		`tabSales Invoice Payment` sp, `tabEmployee` e
	WHERE
		e.user_id = sp.owner
		AND sp.mode_of_payment = %(mode_of_payment)s
		AND sp.modified BETWEEN %(from_date)s AND %(to_date)s
		AND sp.docstatus = 1
	Group By e.owner
	ORDER BY
		total_amount desc""",
		filters,
		as_dict=1)
	return data

def get_columns(filters):
	# column depends on the filters
	columns = [
		# Mode of payment
		{
			"fieldname": "name",
			"label": _("نقطة البيع"),
			"fieldtype": "Data",
			"width": 200
		}
	]
	# if filters.group_user:
	# 	columns.extend([
	# 		{
	# 			"fieldname": "employee",
	# 			"label": _(""),
	# 			"fieldtype": "Link",
	# 			"options": "User",
	# 			"width": 200
	# 		}
	# 	]

	# 	)
	if filters.detailed:
		columns.extend([
			{
				"fieldname": "date",
				"label": _(""),
				"fieldtype": "Date",
				"width": 200
			},
			{
				"fieldname": "invoice",
				"label": _(""),
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"width": 200
			},
			{
				"fieldname": "employee",
				"label": _(""),
				"fieldtype": "Data",
				"width": 200
			}
		]
		)
	columns.append(		{
			"fieldname": "total_amount",
			"label": _("إجمالي القيمة"),
			"fieldtype": "Currency",
			"width": 200,
			"precision": 2
		})
	
	return columns