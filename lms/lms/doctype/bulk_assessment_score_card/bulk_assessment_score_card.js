// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Bulk Assessment Score Card", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Bulk Assessment Score Card", {
	refresh(frm) {
		frm.add_custom_button("Reload", function () {
			frm.reload_doc();
		});
		frappe.realtime.on("score_card_progress", (data) => {
			if (data.record_name === frm.doc.name) {
				frm.set_value("track_records", data.progress);
				frm.refresh_field("track_records");

				if (data.generated + data.failed === data.total) {
					
					setTimeout(() => frm.reload_doc(), 1000);
				}
			}
		});
	},
});
