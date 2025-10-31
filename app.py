from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from process import process_files

app = Flask(__name__)
UPLOAD_FOLDER = "input"      # must match process_files
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
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

    return render_template("upload.html")


@app.route("/results")
def show_results():
    files = request.args.get("files", "").split(",")
    return render_template("results.html", files=files)


@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8123, debug=True)
