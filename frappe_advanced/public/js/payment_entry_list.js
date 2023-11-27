function close_pos_shift(listview) {
	// console.log("ButtonFunction");
	// frappe.msgprint("ButtonFunction");
    frappe.call({
        method: 'frappe_advanced.frappe_advanced.api.api.auto_close_shift',
    });
}

frappe.listview_settings['Payment Entry'] = {

	refresh: function(listview) {
        listview.page.add_inner_button(__('إغلاق مناوبة الموظفين'), function() {
            close_pos_shift(listview);
        });
        listview.page.add_inner_button(__('رصيد الخزائن حاليا'), function() {
            frappe.call({
                method: 'frappe_advanced.frappe_advanced.api.api.get_current_balance_msg',
            });
        });
    },
};