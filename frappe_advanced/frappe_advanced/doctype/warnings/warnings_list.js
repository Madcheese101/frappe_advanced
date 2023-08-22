frappe.listview_settings['Warnings'] = {

	add_fields: ["`tabWarnings`.`name`", "`tabWarnings`.`status`",

		"`tabWarnings`.`date`", "`tabWarnings`.`branch`"],

	get_indicator: function (doc) {

		if (doc.status === "Reviewed") {
			return [__("Reviewed"), "green", "status,=,Reviewed"];
		} 
        else if (doc.status === "Pending Review") {
			return [__("Pending Review"), "red", "status,=,Pending Review"];
		}
	},

};