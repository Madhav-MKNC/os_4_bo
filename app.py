from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from processing import process_files
from pre_processing import process_excel_file  # first step

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8123, debug=True)
