# Copyright (c) 2025, MadCheese and contributors
# For license information, please see license.txt

import frappe
from pypika.terms import Case, ValueWrapper

def execute(filters=None):
	columns = get_columns()
	data = []

	data.extend(get_hesham_invoices(filters))
	data.extend(get_oustsanding_invoices())
	data.extend(get_sales(filters))

	return columns, data

def get_hesham_invoices(filters, ):
	data = []
	header = {"name": "محلات هشام", "total_sales": 0, "total_outstanding": 0, "has_value": 1, "indent": 0}
	customers = ["محل بن عاشور", "محل قرقارش"]
	customers_data = []
	for customer in customers:
		customer_header = {"name": customer, "total_sales": 0, "total_outstanding": 0, "has_value": 1, "indent": 1}
		
		selling_header = {"name": "الصادر", "total_sales": 0, "total_outstanding": 0, "has_value": 1, "indent": 2}
		buying_header = {"name": "الوارد", "total_sales": 0, "total_outstanding": 0, "has_value": 1, "indent": 2}

		selling = frappe.qb.get_query("Sales Invoice", 
			fields=[
				"pos_profile as name",
				"sum(grand_total) as total_sales",
				"sum(outstanding_amount) as total_outstanding"
			],
			filters={
				"is_return": 0,
				"docstatus": 1,
				"customer": customer,
				"posting_date": ["between", [filters["from_date"], filters["to_date"]]]
			},
			group_by="pos_profile").run(as_dict=True)
		buying = frappe.qb.get_query("Sales Invoice", 
			fields=[
				"pos_profile as name",
				"sum(grand_total) as total_sales",
				"sum(outstanding_amount) as total_outstanding"
			],
			filters={
				"is_return": 1,
				"docstatus": 1,
				"customer": customer,
				"posting_date": ["between", [filters["from_date"], filters["to_date"]]]
			},
			group_by="pos_profile").run(as_dict=True)
		
		for row in selling:
			selling_header["total_sales"] =  row.get("total_sales", 0)
			selling_header["total_outstanding"] += row.get("total_outstanding", 0)
			row["has_value"] = 0
			row["indent"] = 3

		for row in buying:
			buying_header["total_sales"] += row.get("total_sales", 0)
			buying_header["total_outstanding"] += row.get("total_outstanding", 0)
			row["has_value"] = 0
			row["indent"] = 3
		
		customer_header["total_sales"] = selling_header["total_sales"] + buying_header["total_sales"]
		customer_header["total_outstanding"] = selling_header["total_outstanding"] + buying_header["total_outstanding"]
		header["total_sales"] = selling_header["total_sales"] + buying_header["total_sales"]
		header["total_outstanding"] = selling_header["total_outstanding"] + buying_header["total_outstanding"]

		customers_data.append(customer_header)
		customers_data.append(selling_header)
		customers_data.extend(selling)
		customers_data.append(buying_header)
		customers_data.extend(buying)
	
	data.append(header)
	data.extend(customers_data)
	# data.append(selling_header)
	# data.extend(selling)
	# data.append(buying_header)
	# data.extend(buying)

	return data

def get_oustsanding_invoices():
	header = {"name": "الفواتير الأجلة", "total_sales": 0, "total_outstanding": 0, "has_value": 1, "indent": 0}

	outstanding_sales = frappe.qb.get_query("Sales Invoice", 
		fields=[
			"name",
			"customer",
			"pos_profile",
			"grand_total as total_sales",
			"outstanding_amount as total_outstanding"
		],
		filters={
			# "is_return": 0,
			"docstatus": 1,
			"customer": ["not in", ["محل بن عاشور", "محل قرقارش"]],
			"outstanding_amount": ["!=", 0]
		},
		group_by="pos_profile").run(as_dict=True)
	
	for row in outstanding_sales:
		header["total_sales"] += row["total_sales"]
		header["total_outstanding"] += row["total_outstanding"]
		row["has_value"] = 0
		row["indent"] = 1

	data = [header]
	data.extend(outstanding_sales)
	return data

def get_sales(filters):
	header = {"name": "المبيعات", "total_sales": 0, "total_outstanding": 0, "has_value": 1, "indent": 0}
	
	sales = frappe.qb.get_query("Sales Invoice", 
		fields=[
			"pos_profile as name",
			"sum(grand_total) as total_sales",
			"sum(outstanding_amount) as total_outstanding"
		],
		filters={
			# "is_return": 0,
			"docstatus": 1,
			# "customer": ["not in", ["محل بن عاشور", "محل قرقارش"]],
			"posting_date": ["between", [filters["from_date"], filters["to_date"]]]
		},
		group_by="pos_profile").run(as_dict=True)
	
	for row in sales:
		header["total_sales"] += row["total_sales"]
		header["total_outstanding"] += row["total_outstanding"]
		row["has_value"] = 0
		row["indent"] = 1

	data = [header]
	data.extend(sales)
	return data

def get_columns():
	columns = [
		{
			"fieldname": "name",
			"label": "الوصف",
			"fieldtype": "Data",
			"width": 300
		},
		{
			"fieldname": "total_sales",
			"label": "إجمالي المبيعات",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 200
		},
		{
			"fieldname": "total_outstanding",
			"label": "إجمالي المبلغ المتبقي",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 200
		},
		{
			"fieldname": "customer",
			"label": "الزبون",
			"fieldtype": "Data",
			"width": 300
		},
		{
			"fieldname": "pos_profile",
			"label": "نقطة البيع",
			"fieldtype": "Data",
			"width": 300
		}
	]
	return columns