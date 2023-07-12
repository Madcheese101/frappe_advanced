from datetime import datetime

import frappe
from frappe import _
from erpnext.accounts.utils import get_balance_on

def account_closed_check():
    # accounts = frappe.db.get_list('Mode of Payment Account',
    #                               fields=['default_account'], 
    #                               filters={'default_account':["like","%محل%"]},
    #                               pluck='default_account')
    
    excluded = frappe.db.get_single_value('Advanced Settings', 'exclude_account_numbers').split(",")
    days_limit = frappe.db.get_single_value('Advanced Settings', 'account_transfer_days_limit')
    today = datetime.today().date()
    
    if(days_limit and days_limit > 0):
        #get accounts that descend from a account group
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
                if(any(ele not in account.parent_account for ele in excluded)):
                    balance = get_balance_on(account.name)
                    last_entry_date = frappe.db.get_value('Payment Entry',
                                                        {'paid_from':account.name}, #filter
                                                        ['posting_date']) #filed to retrieve
                    
                    if (last_entry_date):
                        days_diff = (today - last_entry_date).days
                        last_warning = frappe.db.get_value('Warnings',
                                                        {'warning_type':'Account not Transferred',
                                                            'last_transfer_date':last_entry_date,
                                                            'account_name':account.name},
                                                            ['last_transfer_date'])
                        
                        if (balance > 0 
                            and (days_diff > days_limit) 
                            and account.branch 
                            and not last_warning):
                            warning = frappe.get_doc(doctype='Warnings',
                                                warning_type='Account not Transferred',
                                                branch=account.branch,
                                                account_name=account.name,
                                                account_amount=balance,
                                                last_transfer_date=last_entry_date)
                            warning.insert(ignore_permissions=True)
        else:
            print("No accounts")