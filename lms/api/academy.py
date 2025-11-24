import frappe
import csv
from frappe.utils.file_manager import get_file
from frappe.utils.xlsxutils import read_xlsx_file_from_attached_file
import os
import zipfile
from frappe.utils import get_site_path
from frappe.utils.file_manager import save_file
from frappe.utils.pdf import get_pdf



@frappe.whitelist()
def start_import():
    doc = frappe.get_doc("Data Entry - Batch-wise Semester Scores")

    if not doc.import_file:
        frappe.throw("Please upload a file first (.xlsx or .csv).")

    file_name, file_content = get_file(doc.import_file)

    # Read Excel or CSV
    if file_name.endswith(('.xlsx', '.xlsm')):
        rows = read_xlsx_file_from_attached_file(doc.import_file)
    elif file_name.endswith('.csv'):
        content = file_content.decode('utf-8').splitlines()
        rows = list(csv.reader(content))
    else:
        frappe.throw("Invalid file format. Upload .xlsx or .csv.")

    if not rows:
        frappe.throw("Uploaded file is empty.")

    headers = [(h or "").strip() for h in rows[0]]
    data_rows = rows[1:]

    inserted_count = 0
    updated_count = 0

    # Your required subject order
    subject_order = [
        "NF",
        "Own field",
        "OR",
        "CT",
        "CRV",
        "LMS",
        "Managing Farms",
        "Food Systems",
        "DNF",
        "Research Methods"
    ]

    for row in data_rows:
        row_dict = dict(zip(headers, row))

        # Check existing
        existing_doc = frappe.db.get_value(
            "Assessment Score Data",
            {
                "semester": doc.semester,
                "batch": doc.batch,
                "district": row_dict.get("District"),
                "name1": row_dict.get("Name")
            },
            "name"
        )
        print("existing_doc"*20, row_dict.get("Name"),row_dict.get("Frappe ID"))

        if existing_doc:
            new_doc = frappe.get_doc("Assessment Score Data", existing_doc)
            updated_count += 1
        else:
            new_doc = frappe.new_doc("Assessment Score Data")
            inserted_count += 1

        district_code = frappe.db.get_value("District", {"district_name": row_dict.get("District")}, "name")
        # --------------------------------------
        # MAIN STUDENT FIELDS
        # --------------------------------------
        new_doc.batch = doc.batch
        new_doc.semester = doc.semester
        new_doc.district = row_dict.get("District")
        new_doc.name1 = row_dict.get("Name")
        new_doc.mobile_number = row_dict.get("Mobile number")
        new_doc.frappe_id = row_dict.get("Frappe ID")    
        new_doc.assessment_year = row_dict.get("Assessment Year")
        new_doc.custom_designation = row_dict.get("Designation")
        new_doc.designation = row_dict.get("Designation")
        new_doc.issue_date=doc.issue_date
        if district_code:
            new_doc.district_name = district_code
        

        # --------------------------------------
        # DYNAMIC SUBJECT DETECTION
        # --------------------------------------
        subjects = {}

        for header in headers:
            if " - " not in header:
                continue

            subject_name, field_name = header.split(" - ", 1)
            subject_name = subject_name.strip()
            field_name = field_name.strip()

            if subject_name not in subjects:
                subjects[subject_name] = {}

            subjects[subject_name][field_name] = row_dict.get(header)

        # Remove existing subject rows
        new_doc.set("scorecard", [])

        # --------------------------------------
        # APPEND IN CUSTOM ORDER
        # --------------------------------------
        for subject_name in subject_order:
            if subject_name not in subjects:
                continue  # Skip subject that does not exist for this student

            fields = subjects[subject_name]

            new_doc.append("scorecard", {
                "subject_name": fields.get("Subject Name"),
                "subject_code": fields.get("Subject Code"),
                "credits": fields.get("Credits"),
                "continuous_assessment": (
                    fields.get("Continue Assessment (70)") or
                    fields.get("Continuous Assessment (70)")
                ),
                "end_assessment": fields.get("End Assessment (30)")
            })

        # Save
        if existing_doc:
            new_doc.save(ignore_permissions=True)
        else:
            new_doc.insert(ignore_permissions=True)

    frappe.db.commit()
    return f"{inserted_count} inserted • {updated_count} updated successfully."





@frappe.whitelist()
def generate_bulk_score_card(semester=None, batch=None, district=None):
   
   
   
    filters = {
        "semester": semester,
        "batch": batch,
        **({"district_name": district} if district else {}) 
    }
    score_data_exists = frappe.db.exists(
        "Assessment Score Data", filters
    )
    
    msg=f"No Assessment Score Data found for the given Semester and Batch."
    if district:
        msg=f"No Assessment Score Data found for the given Semester, Batch and District: {district}."  
    if not score_data_exists:
        frappe.throw(msg)

    doc = frappe.get_doc({
            "doctype": "Bulk Assessment Score Card",
            "user": frappe.session.user,
            "request_date": frappe.utils.now_datetime(),
            "semester": semester,
            'district': district,
            "batch": batch,
            "status": "Pending",
        })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()    

    frappe.enqueue(
        background_generate_score_cards,
        semester=semester,
        batch=batch,
        record_name= doc.name,
        district_name=district,
        queue="long",
        timeout=3600,
        job_id=f"Generate Score Cards {semester}-{batch}"
    )
    return {
            "success": True,
            "message": "Bulk score card generation started in background.",
            "record": doc.name,
        }



@frappe.whitelist()
def background_generate_score_cards(record_name=None, semester=None, batch=None,district_name=None,assessment_name=None):
    """
    Background job:
    Generate individual PDF score cards for all Assessment Score Data filtered
    by semester and batch, attach them to each record, and create a ZIP file
    attached to a new 'Bulk Assessment Score Card' record.
    """


    frappe.log_error(f"🚀 Starting bulk score card generation | Semester: {semester}, Batch: {batch}", "Bulk Score Card Generation")

    try:
        if not semester or not batch:
            frappe.throw("Please provide both semester and batch.")

        # 🔹 1️⃣ Fetch Assessment Score Data
        filters = {
            "semester": semester,
            "batch": batch,
            **({"district_name": district_name} if district_name else {}),
            **({"name": assessment_name} if assessment_name else {})
        }
        records = frappe.get_all(
            "Assessment Score Data",
            filters=filters,
            fields=["name"],
            # limit=2  # optional for testing
        )

        if not records:
            _update_bulk_record(record_name, "Failed", None)
            return {"success": False, "message": "No Assessment Score Data found."}
        if not assessment_name:
            _update_bulk_record(record_name, "Processing")

        uploaded_files = []
        pdf_filepaths = []
        total_records = len(records)
        generated_count = 0
        failed_count = 0

        # 🔹 2️⃣ Generate PDFs and track progress
        for rec in records:
            try:
                doc = frappe.get_doc("Assessment Score Data", rec.name)
                frappe.log_error(f"Generating PDF for {doc.name}", "Bulk Score Card Generation")

                pdf_template = frappe.get_doc("Print Format", "Assessment Score Data").html
                html_content = frappe.render_template(pdf_template, {"doc": doc})
                pdf_bytes = get_pdf(html_content)
                filename = f"{doc.name1 or doc.name}-{batch}-{semester}-.pdf"
                filepath = os.path.join(get_site_path("private", "files"), filename)

                with open(filepath, "wb") as f:
                    f.write(pdf_bytes)

                pdf_filepaths.append(filepath)

               
                uploaded_file = save_file(
                    filename,
                    open(filepath, "rb").read(),
                    "Assessment Score Data",
                    doc.name,
                    is_private=True
                )

                doc.score_card = uploaded_file.file_url
                doc.save(ignore_permissions=True)
                frappe.db.commit()
            
                
                if assessment_name:
                    return {
                        "success": True,
                        "message": f"PDF generated for {doc.name}.",
                        "file_url": uploaded_file.file_url
                    }

                uploaded_files.append({
                    "docname": doc.name,
                    "file_url": uploaded_file.file_url
                })
               

                generated_count += 1

            except Exception as e:
                failed_count += 1
                frappe.log_error(f"❌ Failed for {rec.name}: {str(e)}", "PDF Generation Error")

            # 🔹 Update progress after each record
            progress_text = f"{generated_count + failed_count} of {total_records} processed ({generated_count} succeeded, {failed_count} failed)"
            
            frappe.db.set_value("Bulk Assessment Score Card", record_name, "track_records", progress_text)
            frappe.db.commit()

            frappe.publish_realtime(
                event='score_card_progress',
                message={
                    'record_name': record_name,
                    'progress': progress_text,
                    'generated': generated_count,
                    'failed': failed_count,
                    'total': total_records
                },
                user=frappe.session.user
            )

        if not pdf_filepaths:
            _update_bulk_record(record_name, "Failed", None)
            frappe.log_error("⚠️ No PDFs generated — ZIP not created or attached.", "Bulk Score Card Generation")
            return {
                "success": False,
                "message": "No PDFs generated, so ZIP was not created.",
                "generated_count": generated_count,
                "failed_count": failed_count
            }
        
        # 🔹 3️⃣ Create ZIP
        zip_filename = f"ScoreCards_({batch}_{semester}).zip"
        zip_path = os.path.join(get_site_path("private", "files"), zip_filename)

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for filepath in pdf_filepaths:
                zipf.write(filepath, os.path.basename(filepath))

        frappe.log_error(f"📦 ZIP created at {zip_path}", "Bulk Score Card Generation")

        # 🔹 4️⃣ Create Bulk Record and Attach ZIP
        bulk_doc = frappe.get_doc("Bulk Assessment Score Card", record_name)
        
        

        if not os.path.exists(zip_path):
            frappe.throw(f"ZIP file not found at {zip_path}")

        with open(zip_path, "rb") as zf:
            uploaded_zip = save_file(
                zip_filename,
                zf.read(),
                "Bulk Assessment Score Card",
                bulk_doc.name,
                is_private=True
            )

        bulk_doc.bulk_score_card = uploaded_zip.file_url
        bulk_doc.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.log_error(f"✅ ZIP attached to Bulk Assessment Score Card: {bulk_doc.name}", "Bulk Score Card Generation")
        _update_bulk_record(record_name, "Complete", uploaded_zip.file_url)

        frappe.publish_realtime(
            event='score_card_progress',
            message={
                'record_name': record_name,
                'progress': "All completed",
                'generated': generated_count,
                'failed': failed_count,
                'total': total_records
            },
            user=frappe.session.user
        )

        return {
            "success": True,
            "message": f"Generated {generated_count}/{total_records} PDFs. ZIP uploaded successfully.",
            "zip_url": uploaded_zip.file_url,
            "files": uploaded_files
        }

    except Exception:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Bulk Score Card Generation Error"
        )
        _update_bulk_record(record_name, "Failed", None)
        return {
            "success": False,
            "error": "An unexpected error occurred. Check logs for details."
        }


def _update_bulk_record(record_name, status, file_url=None):
    try:
        if not record_name:
            return

        doc = frappe.get_doc("Bulk Assessment Score Card", record_name)
        doc.status = status
        if file_url:
            doc.bulk_score_card = file_url
        doc.save(ignore_permissions=True)
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(
            f"Failed to update Bulk Assessment Score Card record {record_name}: {str(e)}",
            "Bulk Assessment Score Card Update"
        )
