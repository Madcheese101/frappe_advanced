from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.utils import get_balance_on
from frappe.utils import today

import json
from six import string_types

from erpnext.controllers.item_variant import copy_attributes_to_variant, generate_keyed_value_combinations, get_variant
from frappe.utils import cstr


@frappe.whitelist()
def get_current_user_defaults():
    branch, default_warehouse, default_in_transit_warehouse, letter_head = ["","","",""]
    
    if(frappe.session.user != "Administrator"):
        branch, default_warehouse, default_in_transit_warehouse = frappe.db.get_value('Employee', {'user_id': frappe.session.user}, 
			['branch', 'default_warehouse', 
			'default_in_transit_warehouse'])
        letter_head = frappe.db.get_value('Branch', branch, ['letter_head'])
	
    return {"branch": branch or "",
            "default_warehouse": default_warehouse or "", 
            "default_in_transit_warehouse": default_in_transit_warehouse or "", 
            "letter_head": letter_head or ""}

@frappe.whitelist()
def set_title(title, doc_name):
    frappe.db.set_value('Stock Entry', doc_name, {
        'title': title
    })
    frappe.db.commit()
    return True

@frappe.whitelist()
def auto_close_shift():
    posawesome_exists = "posawesome" in frappe.get_installed_apps()
    if posawesome_exists:
        posProfile =  frappe.db.get_list('POS Profile',
                            pluck="name")
        if posProfile and len(posProfile) == 1:
            from posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift import (
                make_closing_shift_from_opening,
                submit_closing_shift
                )
            
            filters = {'status': 'Open', 
                    'docstatus': 1,
                    'pos_profile': posProfile[0],
                    'pos_closing_shift': ['in', ['', None]]}
            opening_shifts =  frappe.db.get_all('POS Opening Shift',
                                filters=filters,
                                pluck="name")
            
            if len(opening_shifts) > 0:
                for open_shift in opening_shifts:
                    open_doc = vars(frappe.get_doc("POS Opening Shift", open_shift))
                    closing_doc = make_closing_shift_from_opening(open_doc)
                    
                    for payment in closing_doc.payment_reconciliation:
                        payment.closing_amount = payment.expected_amount
                        payment.difference = 0
                        
                    submit_closing_shift(vars(closing_doc))
                frappe.msgprint("تم إغلاق مناوبات الموظفين")
            else:
                frappe.msgprint('لا يوجد مناوبات لإغلاقها')
        else:
            frappe.msgprint('المستخدم ليس موظف مبيعات')

@frappe.whitelist()
def get_current_balance_msg():
	branches = frappe.db.get_list("Branch", pluck='name')
	msg = ''

	for branch in branches:
		m_payments = frappe.db.get_list("Mode of Payment", pluck='name', filters={'branch':branch})
		
		if len(m_payments) == 0:
			continue

		accounts_list = frappe.db.get_all("Mode of Payment Account", filters={'parent': ['in', m_payments]}, fields=['default_account', 'parent'])
		msg += branch + ': <br>' + '<ul>'
		for account in accounts_list:
			balance = get_balance_on(account.default_account, today(), ignore_account_permission=True) or 0
			msg += f'<li>{account.parent}: {frappe.format_value(balance, {"fieldtype":"Currency"})} </li>'
		msg += '</ul>'

	if len(branches) > 1:
		middle_man_accounts = frappe.db.get_all("Mode of Payment Account", fields=['default_account', 'parent'], filters={'parent':['like', '%علي%']})
		msg += 'حساب عمي علي: <br>' + '<ul>'
		for account in middle_man_accounts:
			balance = get_balance_on(account.default_account, today(), ignore_account_permission=True) or 0
			msg += f'<li>{account.parent}: {frappe.format_value(balance, {"fieldtype":"Currency"})} </li>'
		msg += '</ul>'

	# parent_accounts = None
	# branch = frappe.db.get_value('Employee', {'user_id': frappe.session.user}, ['branch'])
	# if branch:
	# 	parent_accounts = frappe.db.get_list('Branch', 
	# 						filters={
	# 							'name': branch,
	# 							},
	# 						fields=['parent_account as name', 'parent_account as account_name'])
	# else:
	# 	parent_accounts = frappe.db.get_list("Account",
	# 					filters={
	# 						'is_group': 1,
	# 						'account_number': ['in', [1112,1115,
	# 													1116,1117,
	# 													1119,1121]]
	# 						},
	# 					fields=['account_name', 'name'])

	# for parent in parent_accounts:
	# 	msg += parent.account_name + ': <br>' + '<ul>'
	# 	child_accounts = frappe.db.get_list("Account",
	# 					filters={
	# 						'is_group': 0,
	# 						'parent_account': parent.name
	# 						},
	# 					fields=['account_name', 'name'])
	# 	for child in child_accounts:
	# 		balance = get_balance_on(child.name, today(), ignore_account_permission=True) or 0
	# 		msg += f'<li>{child.account_name}: {frappe.format_value(balance, {"fieldtype":"Currency"})} </li>'
	# 	msg += '</ul>'
	frappe.msgprint(msg)
	
@frappe.whitelist()
def custody_account_balance():
	branch = []
	msg = ''
	user_roles = frappe.get_roles(frappe.session.user)
	if("Accounts Manager" in user_roles):
		expense_accounts = frappe.get_all("Branch", 
									filters={"expenses_account": ["!=", None]},
									pluck="expenses_account")
		for account in expense_accounts:
			if msg == '': msg += '<ul>'
			account_balance = get_balance_on(account, today(), ignore_account_permission=True) or 0
			msg += f'<li>{account}: {frappe.format_value(account_balance, {"fieldtype":"Currency"})} </li>'
		if msg != '':
			msg += '</ul>'
		frappe.msgprint(msg)
	else:
		branch = frappe.db.get_value('Employee', 
					{'user_id': frappe.session.user}, ['branch'])
		
		if branch:
			branch_expenses = frappe.db.get_value('Branch', 
							branch, ['expenses_account'])
			balance = get_balance_on(branch_expenses, today(), ignore_account_permission=True) or 0
			frappe.msgprint(str(balance) + " دينار")	
		else:
			frappe.msgprint("حقل فرع الشركة للمستخدم غير محدد")
				
@frappe.whitelist()
def enqueue_multiple_variant_creation(item, args):
	# There can be innumerable attribute combinations, enqueue
	if isinstance(args, string_types):
		variants = json.loads(args)
	total_variants = 1
	for key in variants:
		total_variants *= len(variants[key])
	if total_variants >= 600:
		frappe.throw(_("Please do not create more than 500 items at a time"))
		return
	if total_variants < 10:
		return create_multiple_variants(item, args)
	else:
		frappe.enqueue("erpnext.controllers.item_variant.create_multiple_variants", item=item, args=args, now=frappe.flags.in_test)
		return 'queued'

def create_multiple_variants(item, args):
	count = 0
	if isinstance(args, string_types):
		args = json.loads(args)

	args_set = generate_keyed_value_combinations(args)

	for attribute_values in args_set:
		if not get_variant(item, args=attribute_values):
			variant = create_variant(item, attribute_values)
			variant.save()
			count +=1

	return count

@frappe.whitelist()
def create_variant(item, args):
	if isinstance(args, string_types):
		args = json.loads(args)

	template = frappe.get_doc("Item", item)
	variant = frappe.new_doc("Item")
	variant.variant_based_on = 'Item Attribute'
	variant_attributes = []

	for d in template.attributes:
		variant_attributes.append({
			"attribute": d.attribute,
			"attribute_value": args.get(d.attribute)
		})

	variant.set("attributes", variant_attributes)
	copy_attributes_to_variant(template, variant)
	make_variant_item_code(template.item_code, template.item_name, variant)

	return variant

def make_variant_item_code(template_item_code, template_item_name, variant):
	"""Uses template's item code and abbreviations to make variant's item code"""
	if variant.item_code:
		return

	abbreviations = []
	values = []
	for attr in variant.attributes:
		item_attribute = frappe.db.sql("""select i.numeric_values, v.abbr
			from `tabItem Attribute` i left join `tabItem Attribute Value` v
				on (i.name=v.parent)
			where i.name=%(attribute)s and (v.attribute_value=%(attribute_value)s or i.numeric_values = 1)""", {
				"attribute": attr.attribute,
				"attribute_value": attr.attribute_value
			}, as_dict=True)

		if not item_attribute:
			continue
			# frappe.throw(_('Invalid attribute {0} {1}').format(frappe.bold(attr.attribute),
			#     frappe.bold(attr.attribute_value)), title=_('Invalid Attribute'),
			#     exc=InvalidItemAttributeValueError)

		abbr_or_value = cstr(attr.attribute_value) if item_attribute[0].numeric_values else item_attribute[0].abbr
		abbreviations.append(abbr_or_value)
		values.append(attr.attribute_value)

	if abbreviations:
		variant.item_code = "{0}-{1}".format(template_item_code, "-".join(abbreviations))
		# variant.item_name = "{0}-{1}".format(template_item_name, "-".join(abbreviations))
	
	if values:
		variant.item_name = "{0}-{1}".format(template_item_name, "-".join(values))
	elif abbreviations:
		variant.item_name = "{0}-{1}".format(template_item_name, "-".join(abbreviations))


@frappe.whitelist()
def submit_doc(document):
	load_doc = json.loads(document)
	# frappe.msgprint(load_doc["doctype"])
	doc = frappe.get_doc(load_doc)
	doc.save()
	doc.submit()
	if doc.doctype == "Stock Entry":
		doc.db_set('add_to_transit', 0)

@frappe.whitelist()
def get_expenses_accounts():
	expense_accounts = frappe.get_all("Branch",
								   fields=[
									   "name as branch",
									   "expenses_account", 
									   "(0) as amount",
									   "'' as receipt_date", 
									   "'' as receipt_no"],
									filters={"expenses_account": ["!=", None]}) or []
	return expense_accounts
@frappe.whitelist()
def insert_branch_expense_credit(data, company):
	data = json.loads(data)
	missing_receipts = []
	missing_dates = []
	cost_center, default_cash_account = frappe.db.get_value("Company", company, ["cost_center", "default_cash_account"])
	if not cost_center:
		frappe.throw(_("Please set Cost Center in Company {0}").format(company))
	if not default_cash_account:
		frappe.throw(_("Please set Default Cash Account in Company {0}").format(company))

	for d in data:
		if d["amount"] <= 0:
			continue
		if not d["receipt_no"]:
			missing_receipts.append(d["branch"])
			continue
		if not d["receipt_date"]:
			missing_dates.append(d["branch"])
			continue
		
		doc = frappe.new_doc('Journal Entry')
		doc.voucher_type = "Journal Entry"
		doc.user_remark = "صرف رصيد عهدة للمحل"
		doc.posting_date = d["receipt_date"]
		doc.cheque_no = f'إذن صرف {d["receipt_no"]}'
		doc.cheque_date = d["receipt_date"]
		# money to account
		to_ = {"account":d["expenses_account"],
	 			"cost_center": cost_center,
				"debit_in_account_currency": d["amount"]}
		# money from account
		from_ = {"account":default_cash_account,
	 			"cost_center": cost_center,
				"credit_in_account_currency": d["amount"]}
		
		doc.append("accounts",to_)
		doc.append("accounts",from_)

		doc.save(ignore_permissions=True)
		doc.submit()

	if missing_receipts:
		frappe.msgprint(_("الرجاء ادخال رقم إذن الصرف لعهدة كل من: {0}").format(", ".join(missing_receipts)))
	if missing_dates:
		frappe.msgprint(_("الرجاء ادخال تاريخ إذن الصرف لعهدة كل من: {0}").format(", ".join(missing_dates)))
@frappe.whitelist()
def get_item_warehouses(so_id):
	# The doctype that has the stock levels is Bin
	doc = frappe.get_doc("Sales Order", so_id)
	msg = ""
	for item in doc.get("items"):
		wh_list = frappe.db.get_list('Bin',
			fields=["warehouse","actual_qty"],
			filters={"item_code": item.item_code, "actual_qty": ['>', 0]},
			order_by="actual_qty desc"
			# as_list=True,
			# pluck='warehouse'
			# as_dict=True
			)
		if wh_list:
			msg=msg + item.item_name +"<hr>" + "<ul>"
			for wh in wh_list:
				msg=msg+"<li>"+wh["warehouse"].replace("BC","")+"  ("+str(wh["actual_qty"])+") </li>"
			msg = msg + "</ul><hr>"
			
	if msg:
		frappe.msgprint(msg)
	else:
		frappe.msgprint(_("No Stock found"))