from flask import Blueprint, jsonify, render_template, request, redirect, url_for
import os

from configs import UPLOAD_FOLDER, OUTPUT_FOLDER
from reports.daily_reports import generate_daily_report


daily_reports_routes = Blueprint('daily_reports_routes', __name__)


@daily_reports_routes.route("/daily_reports_generation", methods=["GET", "POST"])
def daily_reports_generation():
    if request.method == "POST":
        zip_file = request.files.get("zip_file")
        
        if not zip_file or not zip_file.filename.endswith(".zip"):
            return "Please upload a valid ZIP file.", 400

        input_path = os.path.join(UPLOAD_FOLDER, zip_file.filename)
        zip_file.save(input_path)

        report_file = generate_daily_report(
            input_path,
            OUTPUT_FOLDER
        )
        return redirect(url_for("general_routes.show_results", files=",".join([report_file])))

    return render_template("daily_reports.html")


