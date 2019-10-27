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
from reports.panelist import aggregate_scores, appearances_by_year, pvp

#region Flask app initialization
app = Flask(__name__)
jinja_options = Flask.jinja_options.copy()
app.jinja_options.update({"trim_blocks": True, "lstrip_blocks": True})
app.create_jinja_environment()
app.url_map.strict_slashes = False
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
    """Generate a current date/timestamp string"""
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
    render_data = {}
    render_data["ga_property_code"] = config_dict["settings"]["ga_property_code"]
    render_data["rendered_at"] = generate_date_time_stamp()
    return render_template("index.html", render_data=render_data)

@app.route("/panelist")
def panelist():
    return redirect(url_for("index"))

@app.route("/panelist/aggregate_scores")
def panelist_aggregate_scores():
    database_connection.reconnect()
    scores = aggregate_scores.retrieve_all_scores(database_connection)
    stats = aggregate_scores.calculate_stats(scores=scores)
    score_spread = aggregate_scores.retrieve_score_spread(database_connection)

    return render_template("panelist/aggregate_scores.html",
                           ga_property_code=config_dict["settings"]["ga_property_code"],
                           stats=stats,
                           score_spread=score_spread,
                           rendered_at=generate_date_time_stamp)

@app.route("/panelist/appearances_by_year")
def panelist_appearances_by_year():
    database_connection.reconnect()
    panelists = appearances_by_year.retrieve_all_appearance_counts(database_connection)
    show_years = appearances_by_year.retrieve_all_years(database_connection)

    return render_template("panelist/appearances_by_year.html",
                           ga_property_code=config_dict["settings"]["ga_property_code"],
                           panelists=panelists,
                           show_years=show_years,
                           rendered_at=generate_date_time_stamp)

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

    return render_template("panelist/pvp.html",
                           ga_property_code=config_dict["settings"]["ga_property_code"],
                           panelists=panelists,
                           results=pvp_results,
                           rendered_at=generate_date_time_stamp())

#endregion

#region Application Initialization
config_dict = load_config()
database_connection = mysql.connector.connect(**config_dict["database"])
database_connection.autocommit = True
time_zone = pytz.timezone("America/Los_Angeles")

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port="9248")

#endregion