from flask import Blueprint, jsonify, render_template, request, send_from_directory

from configs import UPLOAD_FOLDER, OUTPUT_FOLDER


general_routes = Blueprint('general_routes', __name__)


@general_routes.route('/')
def index():
    return render_template("index.html")


@general_routes.route('/keep_alive')
def keep_alive():
    """
    Ping endpoint for uptimerobot for keeping the server alive
    """
    return jsonify({'status': 'online'}), 200


@general_routes.route("/results")
def show_results():
    files = request.args.get("files", "").split(",")
    return render_template("results.html", files=files)


@general_routes.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

