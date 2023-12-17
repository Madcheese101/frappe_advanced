frappe.listview_settings['Payment Entry'] = {

	refresh: function(listview) {
        if (!frappe.user_roles.includes("Accounts Manager")){
            listview.page.add_inner_button(__('إغلاق مناوبة الموظفين'), function() {
                let line_one = 'هذه العملية يجب ان تتم قبل اغلاق اليوم فقط'
                let line_two = 'هل توافق على هذه العملية؟'
                frappe.confirm(line_one+'<br>'+line_two,
                () => {
                    // action to perform if Yes is selected                   
                    frappe.call({
                        method: 'frappe_advanced.frappe_advanced.api.api.auto_close_shift',
                    });
                }, () => {
                    // action to perform if No is selected
                })
            });
        }
        listview.page.add_inner_button(__('رصيد الخزائن حاليا'), function() {
            frappe.call({
                method: 'frappe_advanced.frappe_advanced.api.api.get_current_balance_msg',
            });
        });
    },
};