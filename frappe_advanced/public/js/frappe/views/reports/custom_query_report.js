// Custom code to extend QueryReport class
// To add a direct print report that prints a report
// without showing print options dialog

// // original code is in:  (frappe/public/js/frappe/views/reports/custom_query_report.js)

frappe.views.QueryReport = class extends frappe.views.QueryReport{

    direct_print_report(letter_head=""){
        var print_settings = locals[":Print Settings"]["Print Settings"];
        var default_letter_head =
            locals[":Company"] && frappe.defaults.get_default("company")
                ? locals[":Company"][frappe.defaults.get_default("company")]["default_letter_head"]
                : "";
       
        var with_head = (letter_head || default_letter_head) ? 1 : 0;

        var data = {with_letter_head: with_head, letter_head: letter_head || default_letter_head, orientation: 'Portrait'};

        data = $.extend(print_settings, data);
        if (!data.with_letter_head) {
            data.letter_head = null;
        }
        if (data.letter_head) {
            data.letter_head =
                frappe.boot.letter_heads[print_settings.letter_head];
        }

        const custom_format = this.report_settings.html_format || null;
		const filters_html = this.get_filters_html_for_print();
		const landscape = data.orientation == 'Landscape';
		this.make_access_log('Print', 'PDF');
		frappe.render_grid({
			template: data.columns ? 'print_grid' : custom_format,
			title: __(this.report_name),
			subtitle: filters_html,
			print_settings: data,
			landscape: landscape,
			filters: this.get_filter_values(),
			data: this.get_data_for_print(),
			columns: this.get_columns_for_print(data, custom_format),
			original_data: this.data,
			report: this
		});
	}
}





