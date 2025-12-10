from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from pathlib import Path
import shutil

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'os_1_parser')))

from os_1_parser.main import utils, ms_office, process_addresses, phone_number_lookup

from processing import process_files
from pre_processing import process_excel_file  # first step
from labels.make_labels import generate_label_pdf 

app = Flask(__name__)
UPLOAD_FOLDER = "input"      # must match process_files
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process_csv", methods=["GET", "POST"])
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
            return redirect(url_for("show_results", files=",".join(filenames)))
        except Exception as e:
            return f"OOPS: {e}"

    return render_template("process_csv.html")


@app.route("/results")
def show_results():
    files = request.args.get("files", "").split(",")
    return render_template("results.html", files=files)


@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


# 🆕 COMBINED route: Excel → Preprocessing → CSV → process_files
@app.route("/convert_excel", methods=["GET", "POST"])
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
            return redirect(url_for("show_results", files=",".join(filenames)))

        except Exception as e:
            return f"Error during Excel conversion or processing: {e}", 500

    return render_template("convert_excel.html")


@app.route("/generate_labels", methods=["GET", "POST"])
def generate_labels():
    if request.method == "POST":
        file = request.files.get("file")
        
        # Check if file exists and is a CSV
        if not file or not file.filename.endswith(".csv"):
            return "Please upload a valid CSV file.", 400
        
        # Save input file
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(input_path)

        try:
            # Call function from make_labels.py
            # Pass input path and output folder; Expect back the PDF filename
            output_filename = generate_label_pdf(input_path, OUTPUT_FOLDER)
            
            return redirect(url_for("show_results", files=output_filename))
            
        except Exception as e:
            return f"Error generating labels: {e}", 500

    return render_template("generate_labels.html")


"""
os_1_parser below
"""

def _run_text_to_xlsx_with_flags(flag: str, text_path: str, out_dir: str, enable_sorting: bool | None, verbose: bool) -> str:
    file_text = utils.read_input_file(text_path)
    address_list = process_addresses(file_text, flag=flag, verbose_mode=verbose, enable_sorting=enable_sorting)
    out_xlsx = utils.generate_output_file_path(out_dir, Path(text_path).stem, "xlsx")
    ms_office.export_to_MS_Excel_using_xlsxwriter(address_list=address_list, file_name=out_xlsx)
    return out_xlsx


def write_lookup_file(output_folder):
    """Creates phone_number_lookup.txt from phone_number_lookup.numbers."""
    filepath = Path(output_folder) / "phone_number_lookup.txt"
    numbers = list(map(str, phone_number_lookup.numbers))

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(numbers))

    return filepath


@app.route("/os1_phone", methods=["GET", "POST"])
def os1_phone():
    if request.method == "POST":
        flag = request.form.get("flag")
        if flag not in ["-f", "-m"]:
            return "Invalid flag", 400

        sort_choice = request.form.get("enable_sorting")
        enable_sorting = True if sort_choice == "on" else False
        verbose = request.form.get("verbose") == "on"

        # required main input (.txt)
        main_file = request.files.get("main_file")
        if not main_file or not main_file.filename.endswith(".txt"):
            return "Upload a .txt main file", 400

        main_path = os.path.join(UPLOAD_FOLDER, main_file.filename)
        main_file.save(main_path)

        try:
            out_xlsx = _run_text_to_xlsx_with_flags(
                flag=flag,
                text_path=main_path,
                out_dir=OUTPUT_FOLDER,
                enable_sorting=enable_sorting,
                verbose=verbose
            )

            # always (re)create lookup from in-memory numbers
            lookup_path = write_lookup_file(OUTPUT_FOLDER)

            files = [os.path.basename(out_xlsx), lookup_path.name]
            return redirect(url_for("show_results", files=",".join(files)))

        except Exception as e:
            return f"Error: {e}", 500

    return render_template("os1_phone.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8123, debug=True)
