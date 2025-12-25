from flask import Blueprint, render_template, request, url_for, redirect, send_from_directory
import os

from configs import UPLOAD_FOLDER, OUTPUT_FOLDER
from processing_and_pre_processing.pre_processing import process_excel_file
from processing_and_pre_processing.processing import process_files


processing_and_pre_processing_routes = Blueprint('processing_and_pre_processing_routes', __name__)


@processing_and_pre_processing_routes.route("/process_csv", methods=["GET", "POST"])
def upload_files():
    if request.method == "POST":
        files = request.files.getlist("files")
        saved_files = []

        for f in files:
            if f and f.filename.endswith(".csv"):
                path = os.path.join(UPLOAD_FOLDER, f.filename)
                f.save(path)
                saved_files.append(f.filename)

        if not saved_files:
            return "No CSV files uploaded.", 400

        try:
            output_paths = process_files(saved_files)
            filenames = [os.path.basename(p) for p in output_paths]
            return redirect(url_for("general_routes.show_results", files=",".join(filenames)))
        except Exception as e:
            return f"OOPS: {e}"

    return render_template("process_csv.html")


@processing_and_pre_processing_routes.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


# 🆕 COMBINED route: Excel → Preprocessing → CSV → process_files
@processing_and_pre_processing_routes.route("/convert_excel", methods=["GET", "POST"])
def convert_excel():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename.endswith(".xlsx"):
            return "Please upload a valid Excel (.xlsx) file.", 400

        # Save uploaded Excel
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(input_path)

        try:
            # Step 1️⃣: Run Excel pre-processing to produce intermediate CSV
            intermediate_csv = process_excel_file(input_path)

            # Step 2️⃣: Feed that CSV into main process_files
            intermediate_filename = os.path.basename(intermediate_csv)
            output_paths = process_files([intermediate_filename])

            # Step 3️⃣: Redirect to results or download
            filenames = [os.path.basename(p) for p in output_paths]
            return redirect(url_for("general_routes.show_results", files=",".join(filenames)))

        except Exception as e:
            return f"Error during Excel conversion or processing: {e}", 500

    return render_template("convert_excel.html")

