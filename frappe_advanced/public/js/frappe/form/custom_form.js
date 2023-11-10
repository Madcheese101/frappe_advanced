// custom code to change (print_doc()) to accept a 
// (print format) & (branch) as variables
// and make it possible to directly show print page.

// original code is in:  (frappe/public/js/frappe/form)

frappe.ui.form.Form = class extends frappe.ui.form.Form{
    print_doc(print_format = null, branch = null) {
		let letter_head = '';
		// if branch parameter is not lull
		if(branch != null || branch != ''){
			// get letter head custom field value from
			// said branch in branch doctype.
			frappe.db.get_value('Branch', branch, 'letter_head')
			.then(r => {
				if(r.message.letter_head){
					// if letter head found set 
					// letter head for url string
					letter_head = '&letterhead=' + 
						encodeURIComponent(r.message.letter_head);
				}
			});
		}
		frappe.db.exists("Print Format", print_format).then((result) => {
			if(result && print_format){
				// if print format exist 
				// and print format not empty
				// set url string options
				// and open print window
				let w = window.open(
					frappe.urllib.get_full_url(
						'/printview?' +
							'doctype=' +
							encodeURIComponent(this.doctype) +
							'&name=' +
							encodeURIComponent(this.doc.name) +
							('&trigger_print=1') +
							'&format=' +
							encodeURIComponent(print_format) +
							'&no_letterhead=0' +
							letter_head
					)
				);
				if (!w) {
					frappe.msgprint(__('Please enable pop-ups'));
					return;
				}
				// frappe.route_options = {
				// 	frm: this,
				// 	print_format: print_format,
				// 	branch: branch
				// };
				// frappe.set_route('print', this.doctype, this.doc.name);
			}
			else if(!print_format){
				// if print format is empty or null
				// load print form preview
				frappe.route_options = {
					frm: this,
					print_format: print_format,
					branch: branch
				};
				frappe.set_route('print', this.doctype, this.doc.name);
			}
			else{
				// if print format does not exist then
				// show error
				frappe.throw(('  :لا يوجد ورقة طباعة بهذا الاسم' + 
				"</br>"+
				print_format))
			}
		});

	}
}

