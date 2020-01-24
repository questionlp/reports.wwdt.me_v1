# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""Flask application startup file"""

from datetime import datetime
import json
from typing import Optional, Text
import traceback

from flask import Flask, redirect, render_template, request, Response, url_for
from flask.logging import create_logger
import mysql.connector
import pytz
from werkzeug.exceptions import HTTPException

from reports.guest import best_of_only, scores as guest_scores
from reports.panelist import (aggregate_scores, appearances_by_year,
                              gender_mix, gender_stats,
                              panelist_vs_panelist as pvp,
                              rankings_summary,
                              single_appearance as single,
                              stats_summary,
                              streaks)
from reports.location import average_scores
from reports.scorekeeper import introductions
from reports.show import (all_women_panel, guest_hosts, guest_scorekeeper,
                          lightning_round, show_details)

#region Global Constants
APP_VERSION = "1.4.5.1"
RANK_MAP = {
    "1": "First",
    "1t": "First Tied",
    "2": "Second",
    "2t": "Second Tied",
    "3": "Third"
}
#endregion

#region Flask App Initialization
app = Flask(__name__)
app.url_map.strict_slashes = False
app_logger = create_logger(app)

# Override base Jinja options
app.jinja_options = Flask.jinja_options.copy()
app.jinja_options.update({"trim_blocks": True, "lstrip_blocks": True})
app.create_jinja_environment()

#endregion

#region Bootstrap Functions
def load_config():
    """Load configuration settings from config.json"""
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)

    return config_dict

#endregion

#region Common Functions
def generate_date_time_stamp(time_zone: pytz.timezone = pytz.timezone("UTC")):
    """Generate a current date/timestamp string"""
    now = datetime.now(time_zone)
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")

def current_year(time_zone: pytz.timezone = pytz.timezone("UTC")):
    """Return the current year"""
    now = datetime.now(time_zone)
    return now.strftime("%Y")

#endregion

#region Error Handlers
@app.errorhandler(Exception)
def handle_exception(error):
    """Handle exceptions in a slightly more graceful manner"""
    # Pass through any HTTP errors and exceptions
    if isinstance(error, HTTPException):
        return error

    # Handle everything else with a basic 500 error page
    error_traceback = traceback.format_exc()
    app_logger.error(error_traceback)
    return render_template("errors/500.html",
                           error_traceback=error_traceback), 500

#endregion

#region Default Routes
@app.route("/")
def index():
    """Default landing page"""
    return render_template("index.html")

#endregion

#region Sitemap XML Route
@app.route("/sitemap.xml")
def sitemap_xml():
    """Sitemap XML"""
    sitemap = render_template("core/sitemap.xml")
    return Response(sitemap, mimetype="text/xml")

#endregion

#region Guest Reports
@app.route("/guest")
def get_guest():
    """Redirect /guest to /"""
    return redirect(url_for("index"))

@app.route("/guest/best_of_only")
def guest_best_of_only():
    """Best Of Only Guests Report"""
    database_connection.reconnect()
    guests = best_of_only.retrieve_best_of_only_guests(database_connection)

    return render_template("guest/best_of_only.html", guests=guests)

@app.route("/guest/scoring_exceptions")
def guest_scoring_exceptions():
    """Guest Scoring Exceptions Report"""
    database_connection.reconnect()
    exceptions = guest_scores.retrieve_all_scoring_exceptions(database_connection)

    return render_template("guest/scoring_exceptions.html",
                           exceptions=exceptions)

@app.route("/guest/three_pointers")
def guest_three_pointers():
    """Guest Scoring Three Points Report"""
    database_connection.reconnect()
    three_pointers = guest_scores.retrieve_all_three_pointers(database_connection)

    return render_template("guest/three_pointers.html",
                           three_pointers=three_pointers)

#endregion

#region Location Reports
@app.route("/location")
def get_location():
    """Redirect /location to /"""
    return redirect(url_for("index"))

@app.route("/location/average_scores")
def location_average_scores():
    """Location Average Score Report"""
    database_connection.reconnect()
    locations = average_scores.retrieve_average_scores_by_location(database_connection)

    return render_template("location/average_scores.html",
                           locations=locations)

#endregion

#region Panelist Reports
@app.route("/panelist")
def get_panelist():
    """Redirect /panelist to /"""
    return redirect(url_for("index"))

@app.route("/panelist/aggregate_scores")
def panelist_aggregate_scores():
    """Panelist Aggregate Scores Report"""
    database_connection.reconnect()
    scores = aggregate_scores.retrieve_all_scores(database_connection)
    stats = aggregate_scores.calculate_stats(scores=scores)
    score_spread = aggregate_scores.retrieve_score_spread(database_connection)

    return render_template("panelist/aggregate_scores.html",
                           stats=stats,
                           score_spread=score_spread)

@app.route("/panelist/appearances_by_year")
def panelist_appearances_by_year():
    """Panelist Appearances by Year Report"""
    database_connection.reconnect()
    panelists = appearances_by_year.retrieve_all_appearance_counts(database_connection)
    show_years = appearances_by_year.retrieve_all_years(database_connection)

    return render_template("panelist/appearances_by_year.html",
                           panelists=panelists,
                           show_years=show_years)

@app.route("/panelist/gender_stats")
def panelist_gender_stats():
    """Panelist Statistics by Gender Report"""
    database_connection.reconnect()
    stats = gender_stats.retrieve_stats_by_year_gender(database_connection)
    return render_template("panelist/gender_stats.html", gender_stats=stats)

@app.route("/panelist/losing_streaks")
def panelist_losing_streaks():
    """Panelist Losing Streaks Report"""
    database_connection.reconnect()
    panelists = streaks.retrieve_panelists(database_connection)
    losing_streaks = streaks.calculate_panelist_losing_streaks(panelists,
                                                               database_connection)

    return render_template("panelist/losing_streaks.html",
                           rank_map=RANK_MAP,
                           losing_streaks=losing_streaks)

@app.route("/panelist/panel_gender_mix")
def panelist_panel_gender_mix(gender: Optional[Text] = "female"):
    """Panel Gender Mix Report"""
    database_connection.reconnect()
    gender_tag = gender[0].upper()
    mix = gender_mix.panel_gender_mix_breakdown(gender=gender,
                                                database_connection=database_connection)

    return render_template("panelist/gender_mix.html",
                           panel_gender_mix=mix,
                           gender=gender_tag)

@app.route("/panelist/pvp")
def panelist_pvp_redirect():
    """Panelist vs Panelist Redirect"""
    return redirect(url_for("panelist_pvp_report"), 301)

@app.route("/panelist/panelist_vs_panelist")
def panelist_pvp_report():
    """Panelist vs Panelist Report"""
    database_connection.reconnect()
    panelists = pvp.retrieve_panelists(database_connection)
    panelist_apps = pvp.retrieve_panelist_appearances(panelists=panelists,
                                                      database_connection=database_connection)
    show_scores = pvp.retrieve_show_scores(database_connection)
    pvp_results = pvp.generate_panelist_vs_panelist_results(panelists=panelists,
                                                            panelist_appearances=panelist_apps,
                                                            show_scores=show_scores)

    return render_template("panelist/panelist_vs_panelist.html",
                           panelists=panelists,
                           results=pvp_results)

@app.route("/panelist/rankings_summary")
def panelist_rankings_summary():
    """Panelist Rankings Summary Report"""
    database_connection.reconnect()
    panelists = rankings_summary.retrieve_all_panelists(database_connection)
    rankings = rankings_summary.retrieve_all_panelist_rankings(database_connection)
    return render_template("panelist/rankings_summary.html",
                           panelists=panelists,
                           panelists_rankings=rankings)

@app.route("/panelist/single_appearance")
def panelist_single_appearance():
    """Panelist Single Appearance Report"""
    database_connection.reconnect()
    panelists = single.retrieve_single_appearances(database_connection)
    return render_template("panelist/single_appearance.html",
                           rank_map=RANK_MAP,
                           panelists_appearance=panelists)

@app.route("/panelist/stats_summary")
def panelist_stats_summary():
    """Panelist Statistics Summary Report"""
    database_connection.reconnect()
    panelists = stats_summary.retrieve_all_panelists(database_connection)
    stats = stats_summary.retrieve_all_panelists_stats(database_connection)
    return render_template("panelist/stats_summary.html",
                           panelists=panelists,
                           panelists_stats=stats)

@app.route("/panelist/win_streaks")
def panelist_win_streaks():
    """Panelist Win Streaks Report"""
    database_connection.reconnect()
    panelists = streaks.retrieve_panelists(database_connection)
    win_streaks = streaks.calculate_panelist_win_streaks(panelists=panelists,
                                                         database_connection=database_connection)

    return render_template("panelist/win_streaks.html",
                           rank_map=RANK_MAP,
                           win_streaks=win_streaks)

#endregion

#region Scorekeeper Reports
@app.route("/scorekeeper")
def get_scorekeeper():
    """Redirect /scorekeeper to /"""
    return redirect(url_for("index"))

@app.route("/scorekeeper/introductions")
def scorekeeper_introductions():
    """Scorekeeper Introductions Report"""
    database_connection.reconnect()
    scorekeepers = introductions.retrieve_scorekeepers_with_introductions(database_connection)
    all_introductions = introductions.retrieve_all_scorekeeper_introductions(database_connection)

    return render_template("scorekeeper/introductions.html",
                           scorekeepers=scorekeepers,
                           all_introductions=all_introductions)

#endregion

#region Show Reports
@app.route("/show")
def get_show():
    """Redirect /show to /"""
    return redirect(url_for("index"))

@app.route("/show/all_shows")
def show_all_shows():
    """All Shows Report"""
    ascending = True
    database_connection.reconnect()
    shows = show_details.retrieve_all_shows(database_connection)
    if "sort" in request.args:
        sort = str(request.args["sort"])
        if sort.lower() == "desc":
            shows.reverse()
            ascending = False

    return render_template("/show/all_shows.html",
                           ascending=ascending,
                           shows=shows)

@app.route("/show/all_women_panel")
def show_all_women_panel():
    """All Women Panel Report"""
    database_connection.reconnect()
    shows = all_women_panel.retrieve_shows_all_women_panel(database_connection)

    return render_template("/show/all_women_panel.html",
                           shows=shows)

@app.route("/show/guest_hosts")
def show_guest_hosts():
    """Shows with Guest Hosts Report"""
    database_connection.reconnect()
    shows = guest_hosts.retrieve_shows_guest_host(database_connection)

    return render_template("/show/guest_hosts.html",
                           shows=shows)

@app.route("/show/guest_scorekeepers")
def show_guest_scorekeepers():
    """Shows with Guest Scorekeepers Report"""
    database_connection.reconnect()
    shows = guest_scorekeeper.retrieve_shows_guest_scorekeeper(database_connection)

    return render_template("/show/guest_scorekeepers.html",
                           shows=shows)

@app.route("/show/lightning_round_end_three_way_tie")
def show_lightning_round_end_three_way_tie():
    """Lightning Round Ending in Three-Way Tie Report"""
    database_connection.reconnect()
    shows = lightning_round.shows_ending_with_three_way_tie(database_connection)

    return render_template("/show/lightning_round_end_three_way_tie.html",
                           shows=shows)

@app.route("/show/lightning_round_score_start")
def show_lightning_round_score_start_redirect():
    """Lightning Round Score Start Redirect"""
    return redirect(url_for("show_lightning_round_start_three_way_tie"), 301)

@app.route("/show/lightning_round_start_three_way_tie")
def show_lightning_round_start_three_way_tie():
    """Lightning Round Starting in Three-Way Tie Report"""
    database_connection.reconnect()
    same_start = lightning_round.shows_with_same_lightning_round_start(database_connection)

    return render_template("/show/lightning_round_start_three_way_tie.html",
                           same_start=same_start)

@app.route("/show/original_shows")
def show_original_shows(ascending: Optional[bool] = True):
    """All Original Shows Report"""
    ascending = True
    database_connection.reconnect()
    shows = show_details.retrieve_all_original_shows(database_connection)

    if "sort" in request.args:
        sort = str(request.args["sort"])
        if sort.lower() == "desc":
            shows.reverse()
            ascending = False

    return render_template("/show/original_shows.html",
                           shows=shows,
                           ascending=ascending)

@app.route("/show/original_shows/asc")
def show_original_shows_asc():
    """All Original Shows Report Ascending Redirect"""
    return redirect(url_for("show_original_shows", sort="asc"), 301)

@app.route("/show/original_shows/desc")
def show_original_shows_desc():
    """All Original Shows Report Descending Redirect"""
    return redirect(url_for("show_original_shows", sort="desc"), 301)

#endregion

#region Application Initialization
config = load_config()
app.jinja_env.globals["app_version"] = APP_VERSION
app.jinja_env.globals["ga_property_code"] = config["settings"]["ga_property_code"]
app.jinja_env.globals["rendered_at"] = generate_date_time_stamp
app.jinja_env.globals["current_year"] = current_year
app.jinja_env.globals["site_url"] = config["settings"]["site_url"]
app.jinja_env.globals["stats_url"] = config["settings"]["stats_url"]
database_connection = mysql.connector.connect(**config["database"])
database_connection.autocommit = True

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port="9248")

#endregion
