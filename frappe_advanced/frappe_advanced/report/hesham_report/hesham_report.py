# Copyright (c) 2024, MadCheese and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters):
	customers = ["محل بن عاشور", "محل قرقارش"]
	data = []
	for customer in customers:
		customer_total = get_customer_total(customer, filters) or 0
		data.append({"pos_profile": customer, "grand_total": customer_total, "has_value": 1, "indent":0})
		children = get_children(customer, filters)
		data.extend(children)
		data.append({"pos_profile": "", "has_value": 0, "indent":0})
		

	return data
def get_customer_total(customer, filters):
	data = frappe.get_list("Sales Invoice", filters={
			"customer": customer, 
			"docstatus": 1,
			"outstanding_amount": ["!=", 0],
			"posting_date": ["between", [filters["from_date"], filters["to_date"]]]
		}, 
		fields=["SUM(grand_total) as c_total"],
		group_by="customer",pluck="c_total")
	ctotal = data[0] if data else 0
	return ctotal

def get_children(customer, filters):
	data = []
	types = [{"label": "صادر", "is_return": 0},{"label": "وارد", "is_return": 1}]

	if filters.get("pos_profile"):
		profiles = [filters["pos_profile"]]
	else:
		profiles = frappe.get_list("POS Profile", pluck="name")
	
	
	if filters.get("view_method") == "detailed_by_type":
		for type in types:
			data.append(get_type_total(customer, filters, type))
			data.extend(get_profile_data(customer, filters, profiles, type))
	else:
		data.extend(get_profile_data(customer, filters, profiles))

	return data

def get_type_total(customer, filters, type = None):
	
	data = frappe.get_list("Sales Invoice", 
		filters={
			"customer": customer, 
			"is_return": type["is_return"], 
			"docstatus": 1,
			"posting_date": ["between", [filters["from_date"], filters["to_date"]]],
			"outstanding_amount": ["!=", 0]
		},
		fields=["SUM(grand_total) as t_total"],
		group_by="customer",pluck="t_total")
	t_total = data[0] if data else 0
	return {"pos_profile": type["label"], "grand_total": t_total, "has_value": 1, "indent":1}

def get_profile_data(customer, filters, profiles, type = None):
	data = []
	_filters = {**filters, "posting_date":["between", [filters["from_date"], filters["to_date"]]],
			 "docstatus": 1, "customer": customer, "outstanding_amount": ["!=", 0]}
	if type:
		_filters["is_return"] = type["is_return"]
	
	view_method = filters["view_method"]
	_filters.pop("view_method")
	_filters.pop("from_date")
	_filters.pop("to_date")
	
	for profile in profiles:
		_filters["pos_profile"] =  profile
		data.append(get_profile_total(_filters, view_method))
		data.extend(get_profile_child(_filters, view_method))
	return data


def get_profile_total(filters, view_method):
	has_value = 0 if view_method == "short" else 1
	indent = 2 if view_method == "detailed_by_type" else 1
	
	data = frappe.get_list("Sales Invoice", filters=filters, 
						fields=["SUM(grand_total) as p_total"],
						group_by="customer",pluck="p_total")
	
	p_total = data[0] if data else 0
	return {"pos_profile": filters["pos_profile"], "grand_total": p_total, "has_value": has_value, "indent":indent}

def get_profile_child(filters, view_method):
	indent = 3 if view_method == "detailed_by_type" else 2
	data = []

	if view_method != "short":
		data = frappe.get_list("Sales Invoice", filters=filters, 
				fields=["name as sales_invoice", "posting_date", "status", "grand_total",
			    	"(0) as has_value", f"({indent}) as indent"],
				order_by='posting_date')
	return data


def get_columns():
	columns = [
		{
			"fieldname": "pos_profile",
			"label": _("المحل"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "sales_invoice",
			"label": _("الفاتورة"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 200
		},
		{
			"fieldname": "posting_date",
			"label": _("التاريخ"),
			"fieldtype": "Date",
			"width": 200
		},
		{
			"fieldname": "status",
			"label": _("الحالة"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "grand_total",
			"label": _("الإجمالي"),
			"fieldtype": "Currency",
			"width": 200,
			"precision": 2
		}
	]
	return columns
