#!/usr/bin/env pythno3
# -*- coding: utf-8 -*-

from flask import Flask
import os
from threading import Thread

from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'os_1_parser')))


from blueprints.general_routes import general_routes
from blueprints.label_routes import label_routes
from blueprints.os_1_parser_routes import os_1_parser_routes
from blueprints.processing_and_pre_processing_routes import processing_and_pre_processing_routes
from blueprints.wa_bot_routes import wa_bot_routes
from blueprints.daily_reports_routes import daily_reports_routes

from reports.telegram_bot import bot_thread


# Flask app
app = Flask(__name__)


# Register Blueprints
app.register_blueprint(general_routes)
app.register_blueprint(label_routes)
app.register_blueprint(os_1_parser_routes)
app.register_blueprint(processing_and_pre_processing_routes)
app.register_blueprint(wa_bot_routes)
app.register_blueprint(daily_reports_routes)


def run():
    app.run(host="0.0.0.0", port=8123, debug=False)

def app_thread():
    t = Thread(target=run)
    t.start()


if __name__ == "__main__":
    app_thread()
    bot_thread()
