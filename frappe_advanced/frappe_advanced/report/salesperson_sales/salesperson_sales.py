# Copyright (c) 2025, MadCheese and contributors
# For license information, please see license.txt

import frappe
from frappe import _, throw, _dict, qb
from frappe.query_builder import DocType
from pypika.analytics import Sum
from pypika import Order
from frappe.utils import today, getdate

def execute(filters=None):
	columns = get_columns(filters)
	data = []
	show_cash_only = filters.show_cash_only
	from_date = str(getdate(filters.from_date)) or today()
	to_date = str(getdate(filters.to_date)) or today()

	branchs = filters.branch or frappe.get_all("Branch", pluck="name")

	for branch in branchs:
		branch_total = get_branch_total(branch, show_cash_only, from_date, to_date)

		# if branch_total == 0:
		# 	continue

		data.append({
			"branch": branch,
			"total": branch_total,
			"percentage": 100,
			"indent": 0,
			"has_value": 1})
		data.extend(get_branch_employee_sales(branch, show_cash_only, from_date, to_date, branch_total))
	
	return columns, data


def get_branch_total(branch, show_cash_only, from_date, to_date):
	total_sales = 0
	sales_invoice = DocType('Sales Invoice')
	pos = DocType('POS Profile')
	payments = DocType('Sales Invoice Payment')
	invoice_paid_total = Sum(sales_invoice.paid_amount).as_("total")
	invoice_payment_sum = Sum(payments.amount).as_("total")

	sales_query = (frappe.qb
		.from_(sales_invoice)
		.from_(pos)
		.where(pos.branch == branch)
		.where(sales_invoice.docstatus == 1)
		.where(sales_invoice.pos_profile == pos.name)
		.where(sales_invoice.posting_date.between(from_date, to_date))
		.groupby(sales_invoice.pos_profile)
	)

	payment_entry = DocType('Payment Entry')
	pe_sum = Sum(payment_entry.paid_amount).as_("total")

	pe_query = (frappe.qb
		.from_(payment_entry)
		.select(pe_sum)
		.where(payment_entry.docstatus == 1)
		.where(payment_entry.branch == branch)
		.where(payment_entry.party_type == "Customer")
		.where(payment_entry.payment_type == "Receive")
		.where(payment_entry.posting_date.between(from_date, to_date))
		.groupby(payment_entry.branch))
	
	if show_cash_only:
		sales_query = (sales_query
			.from_(payments)
			.select(invoice_payment_sum)
			.where(sales_invoice.name == payments.parent)
			.where(payments.type == 'Cash')
			.groupby(sales_invoice.pos_profile))
		pe_query = (pe_query
			.where(payment_entry.mode_of_payment_type == 'Cash'))
	else:
		sales_query = (sales_query
			.select(invoice_paid_total))
		
	sales_query_result = sales_query.run(as_dict=True)
	pe_query_result = pe_query.run(as_dict=True)
	if sales_query_result:
		total_sales = total_sales + sales_query_result[0].get("total", 0)
    
	if pe_query_result:
		total_sales = total_sales + pe_query_result[0].get("total", 0)

	return total_sales

def get_branch_employee_sales(branch, show_cash_only, from_date, to_date, branch_total):
	by_sales_inv = get_salesperson_sales(branch, show_cash_only, from_date, to_date) or []
	for employee in by_sales_inv:
		payment_entry_total = get_salesperson_payment_entries(show_cash_only, from_date, to_date, employee.branch)
		employee.total = employee.total + payment_entry_total
		
		employee.percentage = (0 if employee.total == 0 
			else (employee.total / branch_total) * 100)
		employee.indent = 1
		employee.has_value = 0
	
	return by_sales_inv


def get_salesperson_sales(branch, show_cash_only, from_date, to_date):
	sales_invoice = DocType('Sales Invoice')
	pos_profile = DocType('POS Profile')
	employee = DocType('Employee')
	payments = DocType('Sales Invoice Payment')
	paid_amount_total = Sum(sales_invoice.paid_amount).as_("total")
	
	payment_sum = Sum(payments.amount).as_("payments_sum")
	additional_discount_total = Sum(sales_invoice.discount_amount).as_("discount_total")
	total = (payment_sum - additional_discount_total).as_("total")


	query_ = (frappe.qb
		.from_(sales_invoice)
		.from_(pos_profile)
		.from_(employee)
		.select(
			employee.employee_name.as_("branch"),
			sales_invoice.sales_person.as_("sales_person"),
		)
		.where(sales_invoice.docstatus == 1)
		.where(sales_invoice.sales_person == employee.name)
		.where(sales_invoice.posting_date.between(from_date, to_date))
		.where(sales_invoice.pos_profile == pos_profile.name)
		.where(pos_profile.branch == branch)
		.groupby(sales_invoice.sales_person)
	)

	if show_cash_only:
		query_ = (query_
			.from_(payments)
			.select(
				total
			)
			.where(sales_invoice.name == payments.parent)
			.where(payments.type == "Cash")
			.orderby(total, order=Order.desc)
			)
	else:
		query_ = (query_.select(paid_amount_total)
			.orderby(paid_amount_total, order=Order.desc))
	
	result = query_.run(as_dict=1)
	return result

def get_salesperson_payment_entries(show_cash_only, from_date, to_date, employee):
	sales_invoice = DocType('Sales Invoice')
	payment_entry = DocType('Payment Entry')
	reference = DocType('Payment Entry Reference')
	total = Sum(reference.allocated_amount).as_("total")
	
	query_ = (frappe.qb
		.from_(payment_entry)
		.from_(reference)
		.from_(sales_invoice)
		.select(total)
		.where(payment_entry.docstatus == 1)
		.where(payment_entry.party_type == "Customer")
		.where(payment_entry.payment_type == "Receive")
		.where(payment_entry.posting_date.between(from_date, to_date))
		.where(payment_entry.name == reference.parent)
		.where(reference.reference_name == sales_invoice.name)
		.where(sales_invoice.sales_person == employee)
		.groupby(payment_entry.branch))
	
	if show_cash_only:
		query_ = (query_
			.where(payment_entry.mode_of_payment_type == "Cash"))
	
	result = query_.run(as_dict=1)

	if result:
		return result[0].get("total", 0)
	
	return 0

def get_columns(filters):
	# column depends on the filters
	columns = [
		{
			"fieldname": "branch",
			"label": _("الفرع"),
			"fieldtype": "Data",
			"width": 200
		},
		# {
		# 	"fieldname": "employee_name",
		# 	"label": _("الموظف"),
		# 	"fieldtype": "Data",
		# 	"width": 200
		# },
		{
			"fieldname": "total",
			"label": _("الإجمالي"),
			"fieldtype": "Currency",
			"width": 200,
			"precision": 2
		},
		{
			"fieldname": "percentage",
			"label": _("النسبة"),
			"fieldtype": "Percent",
			"width": 200,
			"precision": 2
		}
	]
	return columns