// // custom code to change (print_doc()) to accept a 
// // (print format) & (branch) as variables
// // and insert it to frappe.routing_options

// // original code is in:  (frappe/public/js/frappe/form)

frappe.ui.form.Form = class extends frappe.ui.form.Form{
    print_doc(print_format = null, branch = null) {
		
		frappe.db.exists("Print Format", print_format).then((result) => {
			if(result && print_format){
				frappe.route_options = {
					frm: this,
					print_format: print_format,
					branch: branch
				};
				frappe.set_route('print', this.doctype, this.doc.name);
			}
			else if(!print_format){
				frappe.route_options = {
					frm: this,
					print_format: print_format,
					branch: branch
				};
				frappe.set_route('print', this.doctype, this.doc.name);
			}
			else{
				frappe.throw(('  :لا يوجد ورقة طباعة بهذا الاسم' + 
				"</br>"+
				print_format))
			}
		});

	}
}

