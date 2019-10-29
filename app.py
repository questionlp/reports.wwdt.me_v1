# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""Flask application startup file"""

from datetime import datetime
import json
import os
import pytz
from typing import Optional, Text

import mysql.connector
from mysql.connector.errors import DatabaseError, ProgrammingError
from flask import (Flask, abort, redirect, render_template,
                   render_template_string, request, url_for)
from reports.panelist import (aggregate_scores, appearances_by_year,
                              gender_mix, panelist_vs_panelist)
from reports.location import average_scores
from reports.show import original_shows

#region Flask App Initialization
app = Flask(__name__)
jinja_options = Flask.jinja_options.copy()
app.jinja_options.update({"trim_blocks": True, "lstrip_blocks": True})
app.create_jinja_environment()
app.url_map.strict_slashes = False
#endregion

#region Bootstrap Functions
def load_config():
    """Load configuration settings from config.json"""

    with open("config.json", "r") as config_file:
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
def error_500(error):
    return render_template_string(error)

#endregion

#region Default Routes
@app.route("/")
@app.route("/location")
@app.route("/panelist")
@app.route("/show")
def index():
    return render_template("index.html",
                           ga_property_code= config_dict["settings"]["ga_property_code"],
                           rendered_at=generate_date_time_stamp())

#endregion

#region Static Content Redirect Routes
@app.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="favicon.ico"))

#endregion

#region Location Reports
@app.route("/location/average_scores")
def location_average_scores():
    locations = average_scores.retrieve_average_scores_by_location(database_connection)

    return render_template("location/average_scores.html",
                           ga_property_code=config_dict["settings"]["ga_property_code"],
                           locations=locations,
                           rendered_at=generate_date_time_stamp())

#endregion

#region Panelist Reports
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
                           rendered_at=generate_date_time_stamp())

@app.route("/panelist/appearances_by_year")
def panelist_appearances_by_year():
    database_connection.reconnect()
    panelists = appearances_by_year.retrieve_all_appearance_counts(database_connection)
    show_years = appearances_by_year.retrieve_all_years(database_connection)

    return render_template("panelist/appearances_by_year.html",
                           ga_property_code=config_dict["settings"]["ga_property_code"],
                           panelists=panelists,
                           show_years=show_years,
                           rendered_at=generate_date_time_stamp())

@app.route("/panelist/panel_gender_mix")
def panelist_panel_gender_mix(gender: Optional[Text] = "female"):
    database_connection.reconnect()
    gender_tag = gender[0].upper()
    panel_gender_mix = gender_mix.panel_gender_mix_breakdown(gender=gender,
                                                             database_connection=database_connection)

    return render_template("panelist/gender_mix.html",
                           ga_property_code=config_dict["settings"]["ga_property_code"],
                           panel_gender_mix=panel_gender_mix,
                           gender=gender_tag,
                           rendered_at=generate_date_time_stamp())

@app.route("/panelist/pvp")
def panelist_pvp_redirect():
    return redirect(url_for("panelist_pvp_report"))

@app.route("/panelist/panelist_vs_panelist")
def panelist_pvp_report():
    database_connection.reconnect()
    panelists = panelist_vs_panelist.retrieve_panelists(database_connection)
    panelist_appearances = panelist_vs_panelist.retrieve_panelist_appearances(panelists=panelists,
                                                             database_connection=database_connection)
    show_scores = panelist_vs_panelist.retrieve_show_scores(database_connection)
    pvp_results = panelist_vs_panelist.generate_panelist_vs_panelist_results(panelists=panelists,
                                                            panelist_appearances=panelist_appearances,
                                                            show_scores=show_scores)

    return render_template("panelist/panelist_vs_panelist.html",
                           ga_property_code=config_dict["settings"]["ga_property_code"],
                           panelists=panelists,
                           results=pvp_results,
                           rendered_at=generate_date_time_stamp())

#endregion

#region Show Reports
@app.route("/show/original_shows")
def show_original_shows(ascending: Optional[bool] = True):
    database_connection.reconnect()
    shows = original_shows.retrieve_all_original_shows(database_connection)
    if not ascending:
        shows.reverse()

    return render_template("/show/original_shows.html",
                           ga_property_code=config_dict["settings"]["ga_property_code"],
                           shows=shows,
                           ascending=ascending,
                           rendered_at=generate_date_time_stamp())

@app.route("/show/original_shows/asc")
def show_original_shows_asc():
    return show_original_shows(ascending=True)

@app.route("/show/original_shows/desc")
def show_original_shows_desc():
    return show_original_shows(ascending=False)

#endregion

#region Application Initialization
config_dict = load_config()
database_connection = mysql.connector.connect(**config_dict["database"])
database_connection.autocommit = True
time_zone = pytz.timezone("America/Los_Angeles")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port="9248")

#endregion