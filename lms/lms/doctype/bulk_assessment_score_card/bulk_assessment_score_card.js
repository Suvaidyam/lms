// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Bulk Assessment Score Card", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Bulk Assessment Score Card", {
	refresh(frm) {
		frappe.realtime.on("score_card_progress", (data) => {
			if (data.record_name === frm.doc.name) {
				frm.set_value("track_records", data.progress);
				frm.refresh_field("track_records");

				// frappe.show_progress(
				// 	"Generating Score Cards...",
				// 	data.generated,
				// 	data.total,
				// 	`${data.generated}/${data.total} completed (${data.failed} failed)`
				// );

				if (data.generated + data.failed === data.total) {
					// frappe.hide_progress();
					setTimeout(() => frm.reload_doc(), 1000);
				}
			}
		});
	},
});
