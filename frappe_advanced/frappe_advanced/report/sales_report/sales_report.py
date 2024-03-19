# Copyright (c) 2024, MadCheese and contributors
# For license information, please see license.txt

import frappe
from frappe import _, _dict
from erpnext.accounts.report.general_ledger.general_ledger import (
	get_accounts_with_children,
	get_result_as_list,
	get_account_type_map)
from frappe.utils import cstr, getdate
from erpnext.accounts.report.financial_statements import get_cost_centers_with_children
from erpnext.accounts.report.utils import convert_to_presentation_currency, get_currency
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
	get_dimension_with_children,
)
from collections import OrderedDict

# to cache translations
TRANSLATIONS = frappe._dict()

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_data(report_filters):
	filters = {}
	data = []
	grand_total = 0
	if report_filters.branch:
		filters["name"] = report_filters.branch
	branches = frappe.get_list('Branch', 
							filters=filters, 
							fields=['name', 'parent_account'])
	
	for branch in branches:
		if branch.parent_account:
			report_filters["account"] = branch.parent_account

			detailed_data, total = get_result(report_filters, branch.name)
			grand_total += total
			data.extend(detailed_data)

	data.append({
		"mode_of_payment": ""})
	data.append({
		"mode_of_payment": ""})
	
	data.append({
		"mode_of_payment": "الإجمالي التام",
		"outcome": grand_total})
	return data


def get_result(filters, branch):
	custom_filters = filters
	custom_filters["include_dimensions"] = 1
	custom_filters["group_by"] = "Group by Voucher (Consolidated)"
	custom_filters["include_default_book_entries"] = 1
	accounting_dimensions = get_accounting_dimensions()
	
	gl_entries = get_gl_entries(custom_filters, accounting_dimensions)
	data = get_data_with_opening_closing(custom_filters, gl_entries, branch)
	
	result = get_result_as_list(data, custom_filters)
	total = data[0].outcome
	return result, total or 0

def get_gl_entries(filters, accounting_dimensions):
	currency_map = get_currency(filters)
	select_fields = """, gl.debit, gl.credit, (gl.debit - gl.credit) as outcome, gl.debit_in_account_currency,
		gl.credit_in_account_currency"""

	if filters.get("show_remarks"):
		if remarks_length := frappe.db.get_single_value(
			"Accounts Settings", "general_ledger_remarks_length"
		):
			select_fields += f",substr(gl.remarks, 1, {remarks_length}) as 'remarks'"
		else:
			select_fields += """,gl.remarks"""

	order_by_statement = "order by gl.posting_date, gl.account, gl.creation"

	if filters.get("include_dimensions"):
		order_by_statement = "order by gl.posting_date, gl.creation"
	if filters.get("group_by") == "Group by Voucher":
		order_by_statement = "order by posting_date, voucher_type, voucher_no"
	if filters.get("group_by") == "Group by Account":
		order_by_statement = "order by gl.account, gl.posting_date, gl.creation"
	if filters.get("include_default_book_entries"):
		filters["company_fb"] = frappe.db.get_value(
			"Company", filters.get("company"), "default_finance_book"
		)

	dimension_fields = ""
	if accounting_dimensions:
		dimension_fields = ", ".join(accounting_dimensions) + ","

	# """", 
	# 		emp.employee_name as employee,
	# 		mop.parent as mode_of_payment"""
	gl_entries = frappe.db.sql(
		"""
		select
			gl.name as gl_entry, gl.posting_date, gl.account, gl.party_type, gl.party,
			gl.voucher_type, gl.voucher_no, {dimension_fields}
			gl.cost_center, gl.project,
			gl.against_voucher_type, gl.against_voucher, gl.account_currency,
			gl.against, gl.is_opening, gl.creation,
			mop.parent as mode_of_payment,
			emp.employee_name as employee
			{select_fields}
		from `tabGL Entry` gl

			LEFT JOIN `tabPayment Entry Reference` pe
			ON gl.voucher_no = pe.parent
			
			LEFT JOIN `tabSales Invoice` si
			ON pe.reference_name = si.name
			
			LEFT JOIN `tabEmployee` emp
			ON   CASE
				WHEN gl.voucher_type = 'Payment Entry' THEN si.owner=emp.user_id
			ELSE gl.owner=emp.user_id
			End

			LEFT JOIN `tabMode of Payment Account` mop
			ON gl.account = mop.default_account
		WHERE
		gl.voucher_no not like '%%ACC-INT%%' and 
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
	conditions = [
		"gl.voucher_type in ('Sales Invoice', 'Payment Entry')"
		]

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

def initialize_gle_map(gl_entries, filters):
	gle_map = OrderedDict()
	# will return account, party or voucher_no
	group_by = group_by_field(filters.get("group_by"))

	for gle in gl_entries:
		# will get the value of group_by 
		# value of one of these keys/columns
		# account, party or voucher_no
		key = gle.get(group_by) 
		# if key exist in gle_map then
		gle_map.setdefault(key, _dict(totals=get_totals_dict(), entries=[]))
	return gle_map

def group_by_field(group_by):
	if group_by == "Group by Party":
		return "party"
	elif group_by in ["Group by Voucher (Consolidated)", "Group by Account"]:
		return "account"
	else:
		return "voucher_no"
	
def get_totals_dict():
	def _get_debit_credit_dict(label):
		return _dict(
			account=label,
			debit=0.0,
			credit=0.0,
			debit_in_account_currency=0.0,
			credit_in_account_currency=0.0,
		)

	return _dict(
		opening=_get_debit_credit_dict(_("Opening")),
		total=_get_debit_credit_dict(_("Total")),
		closing=_get_debit_credit_dict(_("Closing")),
	)
	
def get_data_with_opening_closing(filters, gl_entries, branch):
	data = []
	view_method = filters.get("view_method")

	gle_map = initialize_gle_map(gl_entries, filters)
	
	totals = get_accountwise_gle(filters, gl_entries, gle_map)
	
	totals.total.mode_of_payment = branch
	totals.total.has_value = 1
	totals.total.indent = 0
	totals.balance = None
	data.append(totals.total)

	for entry in gle_map:
		if not gle_map[entry].mode_of_payment:
			mode_of_payment = frappe.get_all('Mode of Payment Account',filters={
				"default_account": entry
			},
			pluck="parent")

			if mode_of_payment:
				gle_map[entry].mode_of_payment = mode_of_payment[0]
			else:
				gle_map[entry].mode_of_payment = entry

		
		data.append({
			"mode_of_payment": gle_map[entry].mode_of_payment,
			"debit":gle_map[entry].totals.total.debit,
			"outcome":gle_map[entry].totals.total.outcome or 0.0,
			"has_value": 1,
			"indent": 1
		})

		if view_method == "detailed":
			data.extend(gle_map[entry].entries)
		if view_method == "employee_short":
			if "users" in gle_map[entry]:
				for key, value in gle_map[entry].users.items():
					data.append({
						"employee": key,
						"debit": value,
						"outcome": value,
						"has_value": 0,
						"indent": 2
					})
			# data.append({"employee":})

	return data


def get_accountwise_gle(filters, gl_entries, gle_map):
	totals = get_totals_dict()
	group_by = group_by_field(filters.get("group_by"))
	group_by_voucher_consolidated = filters.get("group_by") == "Group by Voucher (Consolidated)"

	def update_value_in_dict(data, key, gle):
		data[key].debit += gle.debit
		data[key].credit += gle.credit
		if "outcome" not in data[key].keys():
			data[key]["outcome"] = gle.outcome
		else:
			data[key].outcome += gle.outcome

		data[key].debit_in_account_currency += gle.debit_in_account_currency
		data[key].credit_in_account_currency += gle.credit_in_account_currency

		if data[key].against_voucher and gle.against_voucher:
			data[key].against_voucher += ", " + gle.against_voucher

	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	show_opening_entries = filters.get("show_opening_entries")
	view_method = filters.get("view_method")
	
	for gle in gl_entries:
		group_by_value = gle.get(group_by)

		if gle.posting_date < from_date or (cstr(gle.is_opening) == "Yes" and not show_opening_entries):
			if not group_by_voucher_consolidated:
				update_value_in_dict(gle_map[group_by_value].totals, "opening", gle)
				update_value_in_dict(gle_map[group_by_value].totals, "closing", gle)

			update_value_in_dict(totals, "opening", gle)
			update_value_in_dict(totals, "closing", gle)

		elif gle.posting_date <= to_date or (cstr(gle.is_opening) == "Yes" and show_opening_entries):
			if group_by_voucher_consolidated:
				update_value_in_dict(gle_map[group_by_value].totals, "total", gle)
				update_value_in_dict(gle_map[group_by_value].totals, "closing", gle)
				update_value_in_dict(totals, "total", gle)
				update_value_in_dict(totals, "closing", gle)

				# payemnt totals grouped by user:
				if "users" not in gle_map[group_by_value]:
					gle_map[group_by_value].users = {}
				# add amount to user if exist
				if gle.employee in gle_map[group_by_value].users:
					gle_map[group_by_value].users[gle.employee] += gle.outcome
				# create user with initial amount if not exist
				else:
					gle_map[group_by_value].users[gle.employee] = gle.outcome
					
				gle_map[group_by_value].mode_of_payment = (gle.mode_of_payment)
				
				if view_method == "detailed":
					gle.has_value = 0
					gle.indent = 2
					gle.mode_of_payment = gle.employee
					gle.employee = ""

				gle_map[group_by_value].entries.append(gle)

	return totals

def get_columns(filters):
	# column depends on the filters
	columns = [
		{
			"fieldname": "mode_of_payment",
			"label": _("البند"),
			"fieldtype": "Data",
			"width": 200
		}
	]
	
	if filters.view_method == "employee_short":
		columns.extend(	[
			{
				"fieldname": "employee",
				"label": _("الموظف"),
				"fieldtype": "data",
				"width": 150
			},
			{
				"fieldname": "outcome",
				"label": _("إجمالي القيمة"),
				"fieldtype": "Currency",
				"width": 200,
				"precision": 2
			}
		])
	elif filters.view_method == "detailed":
		columns.extend([
			{
				"label": _("Journal Entry"),
				"fieldname": "voucher_no",
				"fieldtype": "Dynamic Link",
				"options": "voucher_type",
				"width": 200
			},
			{
				"fieldname": "outcome",
				"label": _("إجمالي القيمة"),
				"fieldtype": "Currency",
				"width": 150,
				"precision": 2
			},
			{
				"fieldname": "posting_date",
				"label": _("التاريخ"),
				"fieldtype": "Date",
				"width": 120
			}
		])
	else:
		columns.append({
				"fieldname": "outcome",
				"label": _("إجمالي القيمة"),
				"fieldtype": "Currency",
				"width": 200,
				"precision": 2
			})

	return columns