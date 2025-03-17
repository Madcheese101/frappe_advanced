frappe.listview_settings['Journal Entry'] = {
	refresh: function(listview) {
        if (frappe.user_roles.includes("Accounts Manager")){
            listview.page.add_inner_button(__('صرف عهدة'), function() {                
                frappe.call({
                    method: 'frappe_advanced.frappe_advanced.api.api.get_expenses_accounts',
                    callback: function(r) {
                        if (r.message) {
                            expenses_credit_dialog(r.message);
                        }
                    }
                });
            });
            listview.page.add_inner_button(__('دفع المرتبات'), function() {
                frappe.db.get_list('Salary', {
                    fields: ['name as salary_doc_name', 'salaries_total']
                }).then(records => {
                    salary_dialog(records);
                });
            });
        }
    },
};

expenses_credit_dialog = function(accounts){
    const table_fields = [
        { fieldname: 'branch', fieldtype: 'Data', 
            label: 'الفرع', read_only: 1,
            in_list_view: 1},
        { fieldname: 'expenses_account', 
            fieldtype: 'Data', label: 'Account', read_only: 1},
        { fieldname: 'amount', 
            fieldtype: 'Currency', label: 'القيمة', in_list_view: 1, precision:2 },
        { fieldname: 'receipt_date', fieldtype: 'Date', 
            label: 'تاريخ إذن الصرف',
            in_list_view: 1},
        { fieldname: 'receipt_no', fieldtype: 'Data', 
            label: 'رقم إذن الصرف',
            in_list_view: 1},
    ]
    const dialog = new frappe.ui.Dialog({
        title: __("صرف عهدة للفروع"),
        fields: [
            {
                fieldname: "journals",
                fieldtype: "Table",
                label: __(""),
                in_place_edit: true,
                fields: table_fields,
                data: accounts
            },
        ],
        size: "large",
        primary_action: (values) => {
            const journals = values.journals;
            frappe.confirm('هل أنت متأكد من صرف العهدة للفروع؟',
                () => {
                    frappe.call({
                        method: 'frappe_advanced.frappe_advanced.api.api.insert_branch_expense_credit',
                        args:{data: journals, 
                            company: frappe.defaults.get_user_default("Company")}
                    });
                    dialog.hide();
                }, () => {
                    // action to perform if No is selected
                })
        },
        primary_action_label: __("صرف"),
    });
    dialog.show();
}

salary_dialog = function(accounts){
    const table_fields = [
        { fieldname: 'salary_doc_name', fieldtype: 'Data', 
            label: 'الفرع', read_only: 1,
            in_list_view: 1},
        { fieldname: 'salaries_total', 
            fieldtype: 'Currency', label: 'اجمالي المرتبات', read_only: 1, in_list_view: 1},
        { fieldname: 'receipt_date', fieldtype: 'Date', 
            label: 'تاريخ إذن الصرف',
            in_list_view: 1},
        { fieldname: 'receipt_no', fieldtype: 'Data', 
            label: 'رقم إذن الصرف',
            in_list_view: 1},
    ]
    const dialog = new frappe.ui.Dialog({
        title: __("صرف المرتبات"),
        fields: [
            {
                fieldname: "journals",
                fieldtype: "Table",
                label: __(""),
                in_place_edit: true,
                fields: table_fields,
                data: accounts
            },
        ],
        size: "large",
        primary_action: (values) => {
            const journals = values.journals.filter(r => r.receipt_no && r.receipt_date);
            
            frappe.confirm('هل أنت متأكد من صرف  مرتبات الموظفين؟',
                () => {
                    frappe.call({
                        method: 'frappe_advanced.frappe_advanced.doctype.salary.salary.insert_salary_journal_entry',
                        args:{receipt_list: journals}
                    });
                    dialog.hide();
                }, () => {
                    // action to perform if No is selected
                })
        },
        primary_action_label: __("صرف"),
      });
      dialog.show();
}