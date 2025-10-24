// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Data Entry  -  Batch-wise Semester Scores", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Data Entry  -  Batch-wise Semester Scores", {
	refresh(frm) {
		if (frm.doc.import_file) {
			frm.add_custom_button(__("Start Import"), () => {
				frappe.call({
					method: "hrms.api.academy.start_import",
					args: {
						docname: frm.doc.name,
						semester: frm.doc.semester,
						batch: frm.doc.batch,
					},
					freeze: true,
					freeze_message: __("Importing data, please wait..."),
					callback(r) {
						if (r.message) {
							frappe.msgprint(
								__("Imported {0} records successfully", [
									r.message,
								])
							);
							frm.reload_doc();
						}
					},
				});
			});
		}
	},
});