frappe.listview_settings['Expenses'] = {

	refresh: function(listview) {
        listview.page.add_inner_button(__('رصيد العهدة حاليا'), function() {
            frappe.call({
                method: 'frappe_advanced.frappe_advanced.api.api.custody_account_balance',
            });
        });
    },
};