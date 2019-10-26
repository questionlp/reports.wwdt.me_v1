# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""Flask application startup file"""

from datetime import datetime
import json
import os
import pytz

import mysql.connector
from mysql.connector.errors import DatabaseError, ProgrammingError
from flask import (Flask, abort, redirect, render_template,
                   render_template_string, request, url_for)
from reports.panelist import appearances_by_year, pvp

#region Flask app initialization
app = Flask(__name__)
app.url_map.strict_slashes = False
jinja_options = Flask.jinja_options.copy()
app.jinja_options.update({"trim_blocks": True, "lstrip_blocks": True})
app.create_jinja_environment()

#endregion

#region Bootstrap Functions
def load_config():
    """Load configuration settings from config.json"""

    with open('config.json', 'r') as config_file:
        config_dict = json.load(config_file)

    return config_dict

#endregion

#region Common Functions
def generate_date_time_stamp():
    now = datetime.now(time_zone)
    return now.strftime("%A, %B %d, %Y %H:%M:%S %Z")

#endregion

#region Error Routes
@app.errorhandler(404)
def error_404(error):
    return redirect(url_for("index"))

def error_500(error):
    return render_template_string(error)

#endregion

#region Report Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/panelist")
def panelist():
    return redirect(url_for("index"))

@app.route("/panelist/appearances_by_year")
def panelist_appearance_by_year():
    database_connection.reconnect()
    panelists = appearances_by_year.retrieve_all_appearance_counts(database_connection)
    show_years = appearances_by_year.retrieve_all_years(database_connection)
    render_data = {}
    render_data["ga_property_code"] = config_dict["settings"]["ga_property_code"]
    render_data["panelists"] = panelists
    render_data["show_years"] = show_years
    render_data["rendered_at"] = generate_date_time_stamp()

    return render_template("panelist/appearances_by_year.html", render_data=render_data)

@app.route("/panelist/pvp")
@app.route("/panelist/panelistvspanelist")
def panelist_vs_panelist():
    database_connection.reconnect()
    panelists = pvp.retrieve_panelists(database_connection)
    panelist_appearances = pvp.retrieve_panelist_appearances(panelists=panelists,
                                                             database_connection=database_connection)
    show_scores = pvp.retrieve_show_scores(database_connection)
    pvp_results = pvp.generate_panelist_vs_panelist_results(panelists=panelists,
                                                            panelist_appearances=panelist_appearances,
                                                            show_scores=show_scores)
    render_data = {}
    render_data["ga_property_code"] = config_dict["settings"]["ga_property_code"]
    render_data["panelists"] = panelists
    render_data["results"] = pvp_results
    print(pvp_results)
    render_data["rendered_at"] = generate_date_time_stamp()

    return render_template("panelist/pvp.html", render_data=render_data)
#endregion

#region Application Initialization
config_dict = load_config()
database_connection = mysql.connector.connect(**config_dict["database"])
database_connection.autocommit = True
time_zone = pytz.timezone("America/Los_Angeles")

if __name__ == '__main__':    
    app.run(debug=False, host="0.0.0.0", port="9248")

#endregion