from datetime import datetime

import frappe
from frappe import _
from erpnext.accounts.utils import get_balance_on

def account_closed_check():
    if frappe.db.get_single_value('Advanced Settings', 'account_transfer_limit_warning'):        
        excluded = frappe.db.get_single_value('Advanced Settings', 'exclude_account_numbers').split(",")
        days_limit = frappe.db.get_single_value('Advanced Settings', 'account_transfer_days_limit')
        today = datetime.today().date()
        
        if(days_limit and days_limit > 0):
            # get accounts that descend from an account group
            # and is not group and is not in excluded account numbers
            mode_of_payment_accounts = frappe.db.get_list('Mode of Payment Account',
                                    fields=['default_account'],
                                    pluck='default_account')
            
            filters = {'is_group':0, 'name': ['in', mode_of_payment_accounts]}
            if excluded:
                filters['account_number'] = ['not in',excluded]
            
            accounts = frappe.db.get_list('Account', 
                                        fields=['name','parent_account','branch'],
                                        filters=filters,
                                        order_by="account_number")
            if(accounts):
                for account in accounts:
                    # another filter to check if exulded account numbers
                    # are in parent account name.
                    if (excluded):
                        if(any(ele not in account.parent_account for ele in excluded)):
                            insert_account_closed_warning(account, today, days_limit)
                    else:
                        insert_account_closed_warning(account, today, days_limit)

def insert_account_closed_warning(account, today, days_limit):
    balance = get_balance_on(account.name)
    if balance > 0:
        last_entry_date = frappe.db.get_value('Payment Entry',
                                            {'paid_from':account.name, 'docstatus': 1}, #filter
                                            ['posting_date']) #fieled to retrieve
        if (last_entry_date):
            days_diff = (today - last_entry_date).days
        else:
            # if account balance > 0 and no payment entry found
            # then fetch latest sale invoice date
            last_sale_date = frappe.db.get_value('Sales Invoice Payment',
                                            {'account':account.name}, #filter
                                            ['creation']) #fieled to retrieve
            days_diff = (today - last_sale_date.date()).days


        last_warning = frappe.db.get_value('Warnings',
                                            {'warning_type':'Account not Transferred',
                                                'last_transfer_date':last_entry_date,
                                                'account_name':account.name,
                                                'account_balance': balance,
                                                'status': 'Pending Review'},
                                                ['date']
                                                )
        if ((days_diff > days_limit) 
            and account.branch 
            and not last_warning):
            warning = frappe.get_doc(doctype='Warnings',
                                warning_type='Account not Transferred',
                                branch=account.branch,
                                account_name=account.name,
                                account_balance=balance,
                                last_transfer_date=last_entry_date)
            warning.insert(ignore_permissions=True)



def stock_entry_check():
    if frappe.db.get_single_value('Advanced Settings', 'stock_entry_not_accepted_warning'):        
        days_limit = frappe.db.get_single_value('Advanced Settings', 'stock_entry_days_limit')
        today = datetime.today().date()
        branch_list = frappe.db.get_list('Branch', fields=['name'], pluck="name")

        if(days_limit and days_limit > 0):          
            filters = {'per_transferred': ['<', 100],
                        'add_to_transit': 1,
                        'outgoing_stock_entry': '',
                        'docstatus': 1}
            
            stock_entries = frappe.db.get_list('Stock Entry', 
                                        fields=['name','title','posting_date', 'outgoing_stock_entry'],
                                        filters=filters,
                                        order_by="posting_date desc")
            if(stock_entries):
                for stock_entry in stock_entries:
                    last_warning = frappe.db.get_value('Warnings',
                                            {'warning_type':'Stock Entry not Accepted',
                                                'stock_entry':stock_entry.name,
                                                'status': 'Pending Review'},
                                                ['date']
                                                )
                    if stock_entry.title not in branch_list:
                        stock_entry.title = None

                    if not last_warning:
                        days_diff = (today - stock_entry.posting_date).days
                        
                        if ((days_diff > days_limit) and not last_warning):
                            warning = frappe.get_doc(doctype='Warnings',
                                                warning_type='Stock Entry not Accepted',
                                                branch=stock_entry.title,
                                                stock_entry=stock_entry.name)
                            warning.insert(ignore_permissions=True)