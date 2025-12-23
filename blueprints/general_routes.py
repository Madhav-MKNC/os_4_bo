from flask import Blueprint, jsonify, render_template


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

