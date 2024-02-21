# Copyright (c) 2024, MadCheese and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.accounts.report.general_ledger.general_ledger import (
	get_accounts_with_children,
	get_data_with_opening_closing,
	get_result_as_list)
from frappe.utils import cstr, getdate
from erpnext.accounts.report.financial_statements import get_cost_centers_with_children
from erpnext.accounts.report.utils import convert_to_presentation_currency, get_currency
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
	get_dimension_with_children,
)

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_data(report_filters):
	filters = {}
	data = []

	if report_filters.branch:
		filters["name"] = report_filters.branch
	branches = frappe.get_list('Branch', 
							filters=filters, 
							fields=['name','expenses_account'])
	
	for branch in branches:
		if branch.expenses_account:
			report_filters["account"] = branch.expenses_account
			# data.append({
			# 	"expense_name": branch.name,
			# 	# "total_amount": pos_total,
			# 	"indent":0,
			# 	"has_value":1})

			if report_filters.detailed:
				detailed_data = get_result(report_filters,{}, branch.name)
				data.extend(detailed_data)
			else:
				data.extend(get_summary(report_filters, branch.name))

	return data
	
def get_detailed(filters ,branch):
	result = []
	
	fields = [
		   'expense_type as expense_name',
		   'journal_entry',
		   'amount as credit',
		   'posting_date',
		   '(1) as indent',
		   '(0) as has_value']
	result = frappe.get_all("Expenses",
				fields=fields,
				filters={
					"branch": ["in", branch],
					"modified":["between",[filters.from_date, filters.to_date]],
					"docstatus":1},
				order_by="posting_date, expense_type DESC, posting_date")
	
	# get_pos_total = frappe.get_all("Sales Invoice Payment",
	# 			fields=["SUM(amount) as total_amount"],
	# 			filters={
	# 				"mode_of_payment": ["in", payment_modes],
	# 				"modified":["between",[filters.from_date, filters.to_date]],
	# 				"docstatus":1},
	# 			group_by="parentfield",
	# 			pluck="total_amount")
	
	total = 0
	# if get_pos_total:
	# 	total = get_pos_total[0]

	return result

def get_summary(filters ,branch):
	result = []
	
	fields = [
		   'expense_type as expense_name',
		   'SUM(amount) as credit',
		   '(1) as indent',
		   '(0) as has_value']
	result = frappe.get_all("Expenses",
				fields=fields,
				filters={
					"branch": ["in", branch],
					"modified":["between",[filters.from_date, filters.to_date]],
					"docstatus":1},
				group_by="expense_type",
				order_by="expense_type")
	
	# get_pos_total = frappe.get_all("Sales Invoice Payment",
	# 			fields=["SUM(amount) as total_amount"],
	# 			filters={
	# 				"mode_of_payment": ["in", payment_modes],
	# 				"modified":["between",[filters.from_date, filters.to_date]],
	# 				"docstatus":1},
	# 			group_by="parentfield",
	# 			pluck="total_amount")
	
	total = 0
	# if get_pos_total:
	# 	total = get_pos_total[0]

	return result

def get_result(filters, account_details, branch):
	custom_filters = filters
	custom_filters["include_dimensions"] = 1
	custom_filters["group_by"] = "Group by Voucher (Consolidated)"
	custom_filters["include_default_book_entries"] = 1
	accounting_dimensions = get_accounting_dimensions()
	
	gl_entries = get_gl_entries(custom_filters, accounting_dimensions)
	data = get_data_with_opening_closing(custom_filters, {}, accounting_dimensions, gl_entries)
	result = get_result_as_list(data, custom_filters)

	result[0].expense_name = branch
	# frappe.throw(str(data))

	return result

def get_gl_entries(filters, accounting_dimensions):
	currency_map = get_currency(filters)
	select_fields = """, gl.debit, credit, gl.debit_in_account_currency,
		gl.credit_in_account_currency, (1) as indent,
		   (0) as has_value"""

	if filters.get("show_remarks"):
		if remarks_length := frappe.db.get_single_value(
			"Accounts Settings", "general_ledger_remarks_length"
		):
			select_fields += f",substr(gl.remarks, 1, {remarks_length}) as 'remarks'"
		else:
			select_fields += """,gl.remarks"""

	order_by_statement = "order by gl.posting_date, gl.account, gl.creation"

	if filters.get("include_dimensions"):
		order_by_statement = "order by posting_date, creation"

	if filters.get("group_by") == "Group by Voucher":
		order_by_statement = "order by posting_date, voucher_type, voucher_no"
	if filters.get("group_by") == "Group by Account":
		order_by_statement = "order by account, posting_date, creation"

	if filters.get("include_default_book_entries"):
		filters["company_fb"] = frappe.db.get_value(
			"Company", filters.get("company"), "default_finance_book"
		)

	dimension_fields = ""
	if accounting_dimensions:
		dimension_fields = ", ".join(accounting_dimensions) + ","

	gl_entries = frappe.db.sql(
		"""
		select
			gl.name as gl_entry, gl.posting_date, gl.account, gl.party_type, gl.party,
			gl.voucher_type, gl.voucher_no, {dimension_fields}
			gl.cost_center, gl.project,
			gl.against_voucher_type, gl.against_voucher, gl.account_currency,
			gl.against, gl.is_opening, gl.creation, exp.expense_name {select_fields}
		from `tabGL Entry` gl
			LEFT JOIN `tabExpense Type` exp
			ON gl.against = exp.account
		WHERE
		gl.company=%(company)s {conditions}
		{order_by_statement}
	""".format(
			dimension_fields=dimension_fields,
			select_fields=select_fields,
			conditions=get_conditions(filters),
			order_by_statement=order_by_statement,
		),
		filters,
		as_dict=1,
	)

	if filters.get("presentation_currency"):
		return convert_to_presentation_currency(gl_entries, currency_map)
	else:
		return gl_entries

def get_conditions(filters):
	conditions = []

	if filters.get("account"):
		filters.account = get_accounts_with_children(filters.account)
		conditions.append("gl.account in %(account)s")

	if filters.get("cost_center"):
		filters.cost_center = get_cost_centers_with_children(filters.cost_center)
		conditions.append("gl.cost_center in %(cost_center)s")

	if filters.get("voucher_no"):
		conditions.append("gl.voucher_no=%(voucher_no)s")

	if filters.get("group_by") == "Group by Party" and not filters.get("party_type"):
		conditions.append("gl.party_type in ('Customer', 'Supplier')")

	if filters.get("party_type"):
		conditions.append("gl.party_type=%(party_type)s")

	if filters.get("party"):
		conditions.append("gl.party in %(party)s")

	if not (
		filters.get("account")
		or filters.get("party")
		or filters.get("group_by") in ["Group by Account", "Group by Party"]
	):
		conditions.append("(gl.posting_date >=%(from_date)s or gl.is_opening = 'Yes')")

	conditions.append("(gl.posting_date <=%(to_date)s or gl.is_opening = 'Yes')")

	if filters.get("project"):
		conditions.append("gl.project in %(project)s")

	if filters.get("include_default_book_entries"):
		if filters.get("finance_book"):
			if filters.get("company_fb") and cstr(filters.get("finance_book")) != cstr(
				filters.get("company_fb")
			):
				frappe.throw(_("To use a different finance book, please uncheck 'Include Default FB Entries'"))
			else:
				conditions.append("(gl.finance_book in (%(finance_book)s, '') OR gl.finance_book IS NULL)")
		else:
			conditions.append("(gl.finance_book in (%(company_fb)s, '') OR gl.finance_book IS NULL)")
	else:
		if filters.get("finance_book"):
			conditions.append("(gl.finance_book in (%(finance_book)s, '') OR gl.finance_book IS NULL)")
		else:
			conditions.append("(gl.finance_book in ('') OR gl.finance_book IS NULL)")

	# if not filters.get("show_cancelled_entries"):
	conditions.append("gl.is_cancelled = 0")

	from frappe.desk.reportview import build_match_conditions

	match_conditions = build_match_conditions("GL Entry")

	if match_conditions:
		conditions.append(match_conditions.replace('`tabGL Entry`','gl'))

	accounting_dimensions = get_accounting_dimensions(as_list=False)

	if accounting_dimensions:
		for dimension in accounting_dimensions:
			# Ignore 'Finance Book' set up as dimension in below logic, as it is already handled in above section
			if not dimension.disabled and dimension.document_type != "Finance Book":
				if filters.get(dimension.fieldname):
					if frappe.get_cached_value("DocType", dimension.document_type, "is_tree"):
						filters[dimension.fieldname] = get_dimension_with_children(
							dimension.document_type, filters.get(dimension.fieldname)
						)
						conditions.append("{0} in %({0})s".format(dimension.fieldname))
					else:
						conditions.append("{0} in %({0})s".format(dimension.fieldname))

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_columns(filters):
	# column depends on the filters
	columns = [
		{
			"fieldname": "expense_name",
			"label": _("البند"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "credit",
			"label": _("القيمة المصروفة"),
			"fieldtype": "Currency",
			"width": 120,
			"precision": 2
		}
	]
	
	if filters.detailed:
		columns = [
			{
				"fieldname": "expense_name",
				"label": _("البند"),
				"fieldtype": "Data",
				"width": 200
			},
			{
				"fieldname": "voucher_no",
				"label": _("Journal Entry"),
				"fieldtype": "Link",
				"options": "Journal Entry",
				"width": 120
			},
			{
				"fieldname": "credit",
				"label": _("القيمة المصروفة"),
				"fieldtype": "Currency",
				"width": 120,
				"precision": 2
			},
			{
				"fieldname": "balance",
				"label": _("الرصيد المتبقي"),
				"fieldtype": "Currency",
				"width": 150,
				"precision": 2
			},
			{
				"fieldname": "posting_date",
				"label": _("التاريخ"),
				"fieldtype": "Date",
				"width": 200
			}
		]
	
	return columns