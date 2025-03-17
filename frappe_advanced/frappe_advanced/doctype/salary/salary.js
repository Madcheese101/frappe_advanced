// Copyright (c) 2025, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Salary', {
	refresh: function(frm) {
		// remove delete row btn
		if(!frappe.user.has_role('System Manager')){
			$('*[data-fieldname="employees"]').find('.grid-remove-rows').hide();
		}

		const btn_grp_label = __('إجراءات سريعة');
		
		if(!frm.is_new()){
			frm.add_custom_button(
				__('تحويل موظف'),
				() => frm.events.transfer_emp(frm),
				btn_grp_label
			);
			frm.add_custom_button(
				__('مغادرة موظف'),
				() => frm.events.emp_leave(frm),
				btn_grp_label
			);
		}

	},

	emp_leave: async function(frm) {
		const emp_name = await emp_leave_prompt(frm.doc.employees);
		const selected_emp = frm.doc.employees.find(emp => emp.emp_name === emp_name);
		
		frappe.confirm('هل تريد ايقاف الموظف ' + emp_name + '؟',
			() => {
				// action to perform if Yes is selected
				frm.call('transfer_employee', {
					selected_emp: selected_emp,
				}).then(() => {
					frm.refresh();
				});
			}, () => {
				// action to perform if No is selected
			})
		console.log('emp_leave');
	},

	transfer_emp: async function(frm) {	
		const transfer_prompt_result = await transfer_emp_prompt(frm.doc.employees, frm.doc.branch);
		const emp_name = transfer_prompt_result.selected_emp;
		const new_branch = transfer_prompt_result.new_branch;
		const selected_emp = frm.doc.employees.find(emp => emp.emp_name === emp_name);
		frappe.confirm('هل تريد تحويل الموظف ' + emp_name + ' لفرع ' + new_branch + '؟',
			() => {
				// action to perform if Yes is selected
				frm.call('transfer_employee', {
					selected_emp: selected_emp,
					new_branch: new_branch
				}).then(() => {
					frm.refresh();
				});
			}, () => {
				// action to perform if No is selected
			})
	},
});

function transfer_emp_prompt(emps, branch) {
    return new Promise((resolve) => {
        frappe.prompt(
            [
                {
                    label: 'الموظف',
                    fieldname: 'selected_emp',
                    fieldtype: 'Select',
                    options: emps.filter(emp => emp.user_id !== frappe.session.user)
									.map(emp => emp.emp_name),
					reqd: 1
                },
				{
                    label: 'الفرع الجديد',
                    fieldname: 'new_branch',
                    fieldtype: 'Link',
                    options: 'Branch',
					reqd: 1,
					ignore_user_permissions: 1,
					get_query: function() {
						return {
							filters: {
								name: ['!=', branch]
							}
						}
					}
                },
            ],
            function(values) {
                resolve(values);
            },
            'الرجاء اختيار الموظف والفرع الجديد',
            "تأكيد"
        );
    });
}

function emp_leave_prompt(emps) {
    return new Promise((resolve) => {
        frappe.prompt(
            [
                {
                    label: 'الحالة',
                    fieldname: 'selected_emp',
                    fieldtype: 'Select',
                    options: emps.filter(emp => emp.user_id !== frappe.session.user)
								.map(emp => emp.emp_name),
					reqd: 1
                }
            ],
            function(values) {
                resolve(values.selected_emp);
            },
            'الرجاء اختيار الموظف المراد مغادرته',
            "تأكيد"
        );
    });
}


frappe.ui.form.on('Employee Manager List', {
    // employees_add(frm, cdt, cdn) {
	// 	console.log(frm.doc.employees)
    // }

	form_render(frm, cdt, cdn){
		if(!frappe.user.has_role('System Manager')){
			frm.fields_dict.employees.grid.wrapper.find('.grid-delete-row').hide();
        // frm.fields_dict.employees.grid.wrapper.find('.grid-duplicate-row').hide();
        // frm.fields_dict.employees.grid.wrapper.find('.grid-move-row').hide();
        // frm.fields_dict.employees.grid.wrapper.find('.grid-append-row').hide();
        // frm.fields_dict.employees.grid.wrapper.find('.grid-insert-row-below').hide();
        // frm.fields_dict.employees.grid.wrapper.find('.grid-insert-row').hide();
		}

    },
	salary(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var total = 0
		frm.doc.employees.forEach(element => {
			total += element.salary;
		});
		frm.set_value('salaries_total', total);
	}
});