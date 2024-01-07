frappe.ui.form.on('Payment Entry', {
    validate: function(frm) {
        if(frm.doc.payment_type == "Receive" && frm.doc.naming_series !== 'ACC-REC-.YYYY.-'){
            msgprint('<p>الرجاء تغيير قيمة حقل</p>'+
            '<p>(Series)(سلسلة التسمية)</p>'+
            '<p>إلى</p>'+
            '<p><span style="color: #ff0000;">ACC-REC-.YYYY.-</span></p>');
            validated = false;
        }
        else if(frm.doc.payment_type == "Pay" && frm.doc.naming_series !== 'ACC-PAY-.YYYY.-'){
            msgprint('<p>الرجاء تغيير قيمة حقل</p>'+
            '<p>(Series)(سلسلة التسمية)</p>'+
            '<p>إلى</p>'+
            '<p><span style="color: #ff0000;">ACC-PAY-.YYYY.-</span></p>');
            validated = false;
        }
        else if(frm.doc.payment_type == "Internal Transfer" && frm.doc.naming_series !== 'ACC-INT-.YYYY.-'){
            msgprint('<p>الرجاء تغيير قيمة حقل</p>'+
            '<p>(Series)(سلسلة التسمية)</p>'+
            '<p>إلى</p>'+
            '<p><span style="color: #ff0000;">ACC-INT-.YYYY.-</span></p>');
            validated = false;
        }
        if(!frappe.user.has_role('Accounts Manager')){
            if(frm.doc.payment_type =='Internal Transfer' && !frm.doc.note_count.includes(frm.doc.mode_of_payment)) {
                msgprint('يجب ان يكون نوع طريقة الإيداع مطابق لطريقة الدفع');
                validated = false;
            }
            if(frm.doc.payment_type =='Internal Transfer' && 
                frm.doc.paid_amount > frm.doc.paid_from_account_balance){
                msgprint('<p>يجب ان يكون قيمة خانة الرصيد المدفوع مطابقة أو أقل من رصيد الخزينة</p>'+
                '<p><span style="color: #ff0000;">الرجاء المراجعة مع قسم المحاسبة/الإدارة</span></p>')
                validated = false;
            }
            if(frm.doc.payment_type =='Internal Transfer' && 
            frm.doc.received_amount != frm.doc.count_total){
                msgprint('<p>يجب ان يكون اجمالي ورقة عد الفئات مطابق لخانة الرصيد المستلم</p>')
                validated = false;
            }
        }
        console.log(frappe.user.has_role('Accounts Manager'))
    },
    payment_type: function(frm) {
        // frm.toggle_reqd('note_count',  frm.doc.payment_type ==='Internal Transfer' && frappe.user_roles.includes("Payment Entry (C)"));
        frm.set_value("paid_amount","");
        frm.set_value("received_amount","");
        frm.set_value("note_count","");
        frm.set_value("mode_of_payment","");

        if(frm.doc.payment_type == "Receive"){
            frm.set_value("naming_series","ACC-REC-.YYYY.-");
        }
        else if(frm.doc.payment_type == "Pay"){
            frm.set_value("naming_series","ACC-PAY-.YYYY.-");
        }
        else if(frm.doc.payment_type == "Internal Transfer"){
            frm.set_value("naming_series","ACC-INT-.YYYY.-");
        }
        frm.refresh_fields();
    },
    note_count: function(frm) {
        if(frm.doc.payment_type ==='Internal Transfer' && frm.doc.paid_from_account_balance !== 0){
            frm.set_value("paid_amount",frm.doc.paid_from_account_balance);
        }
    },
    paid_amount: function(frm) {
        if(frm.doc.payment_type ==='Internal Transfer'){
            frm.set_value("received_amount",frm.doc.count_total);
        }
    },
	mode_of_payment:function(frm) {
	    
	   // frm.toggle_reqd('note_count',  frm.doc.payment_type ==='Internal Transfer' && frappe.user_roles.includes("Payment Entry (C)"));
	    var parentAC_filter = "علي";
	    var payment = (frm.doc.mode_of_payment.split(" ")[0]).slice(0,-1);
	    if(frm.doc.payment_type ==='Internal Transfer'){
	        if(frappe.user_roles.includes("Accounts Manager")){
                payment = "الرئيسية";
                parentAC_filter = "Cash";
                // parentAC_filter = frm.doc.mode_of_payment.substr(frm.doc.mode_of_payment.indexOf(" ") + 1);
            }

        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Account",
                fieldname: "name",
                filters:  [["Account", "parent_account", "like", "%"+parentAC_filter+"%"], 
                            ["Account", "account_name", "like", "%"+payment+"%"]]
            },
            callback: function(r) {
                if (r.message) {
                    if (r.message.name) {
                        frm.set_value("paid_to",r.message.name);
                    }
                }
            }
        });
        frm.refresh_fields();
	    }
    },
    setup: function(frm) {
	    frm.set_query("note_count", function() {
			return {
				filters: [
                    ["Note Count", "docstatus", "=", 1],
                    ["Note Count", "is_advance", "=", 0],
				]
			}
		});
		
		me.frm.set_query("account", "deductions", function(doc, cdt, cdn) {
		return {
            filters: [
                    ["Account", "account_name", "like", "%Write%"]
				]
		};
	});
	}
})