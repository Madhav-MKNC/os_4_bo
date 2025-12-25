from flask import Blueprint, jsonify, render_template, request, redirect, url_for
import os

from configs import UPLOAD_FOLDER, OUTPUT_FOLDER
from labels.make_labels import generate_label_pdf

label_routes = Blueprint('label_routes', __name__)


@label_routes.route("/generate_labels", methods=["GET", "POST"])
def generate_labels():
    if request.method == "POST":
        main_file = request.files.get("file")
        barcode_file = request.files.get("barcode_file")
        
        # Check if file exists and is a CSV
        if not main_file or not main_file.filename.endswith(".csv"):
            return "Please upload a valid CSV file.", 400

        if not barcode_file or not barcode_file.filename.endswith(".json"):
            return "Please upload a valid barcode JSON file.", 400

        # Save input file
        input_path = os.path.join(UPLOAD_FOLDER, main_file.filename)
        main_file.save(input_path)

        barcode_path = os.path.join(UPLOAD_FOLDER, barcode_file.filename)
        barcode_file.save(barcode_path)

        output_filenames = generate_label_pdf(
            input_path,
            OUTPUT_FOLDER,
            barcode_csv_path=barcode_path
        )
        print(output_filenames)
        return redirect(url_for("general_routes.show_results", files=",".join(output_filenames)))

    return render_template("generate_labels.html")

