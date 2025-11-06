// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Assessment Score Data", {
	refresh(frm) {
        let is_save = frm.doc.__unsaved ? false : true;

        if (is_save) {
            frm.add_custom_button("Download PDF", function () {
                if (frm.doc.__unsaved) {
                    frappe.msgprint("Please save the document before downloading the PDF.");
                    return;
                }
				frappe.call({
					method: "lms.api.academy.background_generate_score_cards",
					args: {
						assessment_name: frm.doc.name,
						semester: frm.doc.semester,
						batch: frm.doc.batch,
						district_name: frm.doc.district,
					},
					freeze: true, // show loading indicator
					freeze_message: __("Downloading, please wait..."),
                    callback: function (r) {
                        frappe.dom.unfreeze();
						if (r.message && r.message.file_url) {
							// window.open(r.message.file_url);
							// window.open(r.message);
							const link = document.createElement("a");
							link.href = r.message.file_url;
							link.download = ""; // Let the browser use the original filename
							document.body.appendChild(link);
							link.click();
							document.body.removeChild(link);
						}
					},
				});
			});
        }
			
	},
});
