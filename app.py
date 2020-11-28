# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""Flask application startup file"""

import json
from typing import Optional, Text
import traceback

from flask import Flask, redirect, render_template, request, Response, url_for
from flask.logging import create_logger
import mysql.connector
import pytz
from werkzeug.exceptions import HTTPException

from reports import utility
from reports.guest import (best_of_only,
                           most_appearances,
                           scores as guest_scores)
from reports.host import appearances as h_appearances
from reports.panelist import (aggregate_scores,
                              appearances,
                              appearances_by_year,
                              bluff_stats,
                              gender_mix,
                              gender_stats,
                              panelist_vs_panelist as pvp,
                              panelist_vs_panelist_scoring as pvp_scoring,
                              rankings_summary,
                              single_appearance as single,
                              stats_summary,
                              streaks)
from reports.location import average_scores
from reports.scorekeeper import appearances as sk_appearances
from reports.scorekeeper import introductions
from reports.show import (all_women_panel,
                          guest_hosts,
                          guest_scorekeeper,
                          lightning_round,
                          scoring,
                          search_multiple_panelists as search_mult,
                          show_details)

#region Global Constants
APP_VERSION = "1.11.0"
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

    if "time_zone" in config_dict["settings"] and config_dict["settings"]["time_zone"]:
        time_zone = config_dict["settings"]["time_zone"]
        time_zone_object, time_zone_string = utility.time_zone_parser(time_zone)

        config_dict["settings"]["app_time_zone"] = time_zone_object
        config_dict["settings"]["time_zone"] = time_zone_string
        config_dict["database"]["time_zone"] = time_zone_string
    else:
        config_dict["settings"]["app_time_zone"] = pytz.timezone("UTC")
        config_dict["settings"]["time_zone"] = "UTC"
        config_dict["database"]["time_zone"] = "UTC"

    return config_dict

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
    """Guest Reports Landing Page"""
    return render_template("guest/index.html")

@app.route("/guest/best_of_only")
def guest_best_of_only():
    """Best Of Only Guests Report"""
    database_connection.reconnect()
    guests = best_of_only.retrieve_best_of_only_guests(database_connection)

    return render_template("guest/best_of_only.html", guests=guests)

@app.route("/guest/most_appearances")
def guest_most_appearances():
    """Guests Most Appearances Report"""
    database_connection.reconnect()
    guests = most_appearances.guest_multiple_appearances(database_connection)

    return render_template("guest/most_appearances.html", guests=guests)

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

#region Host Reports
@app.route("/host")
def get_host():
    """Host Reports Landing Page"""
    return render_template("host/index.html")

@app.route("/host/appearance_summary")
def host_appearance_summary():
    """Host Appearances Summary Report"""
    database_connection.reconnect()
    summary = h_appearances.retrieve_appearance_summaries(database_connection)

    return render_template("host/appearance_summary.html", summary=summary)

#endregion

#region Location Reports
@app.route("/location")
def get_location():
    """Location Reports Landing Page"""
    return render_template("location/index.html")

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
    """Panelist Reports Landing Page"""
    return render_template("panelist/index.html")

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

@app.route("/panelist/bluff_stats")
def panelist_bluff_stats():
    """Panelist Bluff the Listener Statistics Report"""
    database_connection.reconnect()
    panelists = bluff_stats.retrieve_all_panelist_bluff_stats(database_connection)

    return render_template("panelist/bluff_stats.html",
                           panelists=panelists)

@app.route("/panelist/first_most_recent_appearances")
def panelist_first_most_recent_appearances():
    """Panelist First and Most Recent Appearances Report"""
    database_connection.reconnect()
    panelists_appearances = appearances.retrieve_first_most_recent_appearances(database_connection)

    return render_template("panelist/first_most_recent_appearances.html",
                           panelists_appearances=panelists_appearances)

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

@app.route("/panelist/panelist_vs_panelist_scoring", methods=["GET", "POST"])
def panelist_pvp_scoring():
    """Panelist vs Panelist Scoring Report"""
    database_connection.reconnect()
    panelists = search_mult.retrieve_panelists(database_connection)

    if request.method == "POST":
        # Parse panelist dropdown selections
        panelist_1 = ("panelist_1" in request.form and request.form["panelist_1"])
        panelist_2 = ("panelist_2" in request.form and request.form["panelist_2"])

        # Create a set of panelist values to de-duplicate values
        deduped_panelists = set([panelist_1, panelist_2])
        if "" in deduped_panelists:
            deduped_panelists.remove("")

        if None in deduped_panelists:
            deduped_panelists.remove(None)

        if len(deduped_panelists) > 0 and deduped_panelists <= panelists.keys():
            # Revert set back to list
            panelist_values = list(deduped_panelists)
            if len(panelist_values) == 2:
                shows = pvp_scoring.retrieve_common_shows(database_connection,
                                                          panelist_values[0],
                                                          panelist_values[1])
                scores = pvp_scoring.retrieve_panelists_scores(database_connection,
                                                               shows,
                                                               panelist_values[0],
                                                               panelist_values[1])
                return render_template("panelist/panelist_vs_panelist_scoring.html",
                                       panelists=panelists,
                                       valid_selections=True,
                                       scores=scores,
                                       rank_map=RANK_MAP)

            # Fallback for invalid panelist selections
            return render_template("panelist/panelist_vs_panelist_scoring.html",
                                   panelists=panelists,
                                   valid_selections=False,
                                   scores=None)

    # Fallback for GET request
    return render_template("panelist/panelist_vs_panelist_scoring.html",
                           panelists=panelists,
                           scores=None)

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
    """Scorekeeper Reports Landing Page"""
    return render_template("scorekeeper/index.html")

@app.route("/scorekeeper/appearance_summary")
def scorekeeper_appearance_summary():
    """Scorekeeper Appearances Summary Report"""
    database_connection.reconnect()
    summary = sk_appearances.retrieve_appearance_summaries(database_connection)

    return render_template("scorekeeper/appearance_summary.html",
                           summary=summary)

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
    """Show Reports Landing Page"""
    return render_template("show/index.html")

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

@app.route("/show/high_scoring")
def show_high_scoring():
    """High Scoring Shows Report"""
    database_connection.reconnect()
    shows = scoring.retrieve_shows_all_high_scoring(database_connection)

    return render_template("/show/high_scoring.html", shows=shows)

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

@app.route("/show/lightning_round_start_end_three_way_tie")
def show_lightning_round_start_end_three_way_tie():
    """Lightning Round Starting and Ending in Three-Way Tie Report"""
    database_connection.reconnect()
    shows = lightning_round.shows_starting_ending_three_way_tie(database_connection)
    return render_template("/show/lightning_round_start_end_three_way_tie.html",
                           shows=shows)

@app.route("/show/lightning_round_start_three_way_tie")
def show_lightning_round_start_three_way_tie():
    """Lightning Round Starting in Three-Way Tie Report"""
    database_connection.reconnect()
    shows = lightning_round.shows_starting_with_three_way_tie(database_connection)

    return render_template("/show/lightning_round_start_three_way_tie.html",
                           shows=shows)

@app.route("/show/lightning_round_start_zero")
def show_lightning_round_start_zero():
    """Lightning Round Starting with Zero Points Report"""
    database_connection.reconnect()
    shows = lightning_round.shows_lightning_round_start_zero(database_connection)

    return render_template("/show/lightning_round_start_zero.html",
                           shows=shows,
                           rank_map=RANK_MAP)

@app.route("/show/lightning_round_zero_correct")
def show_lightning_round_zero_correct():
    """Lightning Round Zero Correct Answers Report"""
    database_connection.reconnect()
    shows = lightning_round.show_lightning_round_zero_correct(database_connection)

    return render_template("/show/lightning_round_zero_correct.html",
                           shows=shows,
                           rank_map=RANK_MAP)

@app.route("/show/low_scoring")
def show_low_scoring():
    """Low Scoring Shows Report"""
    database_connection.reconnect()
    shows = scoring.retrieve_shows_all_low_scoring(database_connection)

    return render_template("/show/low_scoring.html", shows=shows)

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

@app.route("/show/search_multiple_panelists", methods=["GET", "POST"])
def show_search_multiple_panelists():
    """Search Shows by Multiple Selected Panelists"""
    database_connection.reconnect()
    panelists = search_mult.retrieve_panelists(database_connection)

    if request.method == "POST":
        # Parse panelist dropdown selections and checkboxes
        panelist_1 = ("panelist_1" in request.form and request.form["panelist_1"])
        panelist_2 = ("panelist_2" in request.form and request.form["panelist_2"])
        panelist_3 = ("panelist_3" in request.form and request.form["panelist_3"])
        best_of = ("best_of" in request.form and request.form["best_of"] == "on")
        repeats = ("repeats" in request.form and request.form["repeats"] == "on")

        # Create a set of panelist values to de-duplicate values
        deduped_panelists = set([panelist_1, panelist_2, panelist_3])

        # Remove any empty values
        if "" in deduped_panelists:
            deduped_panelists.remove("")

        if None in deduped_panelists:
            deduped_panelists.remove(None)

        if len(deduped_panelists) > 0 and deduped_panelists <= panelists.keys():
            # Revert set back to list
            panelist_values = list(deduped_panelists)
            if len(panelist_values) == 3:
                shows = search_mult.retrieve_matching_three(database_connection,
                                                            panelist_values[0],
                                                            panelist_values[1],
                                                            panelist_values[2],
                                                            best_of,
                                                            repeats)
            elif len(panelist_values) == 2:
                shows = search_mult.retrieve_matching_two(database_connection,
                                                          panelist_values[0],
                                                          panelist_values[1],
                                                          best_of,
                                                          repeats)
            elif len(panelist_values) == 1:
                shows = search_mult.retrieve_matching_one(database_connection,
                                                          panelist_values[0],
                                                          best_of,
                                                          repeats)

            return render_template("/show/search_multiple_panelists.html",
                                   panelists=panelists,
                                   shows=shows)

        # Fallback for no valid panelist(s) selected
        return render_template("/show/search_multiple_panelists.html",
                               panelists=panelists,
                               shows=None)

    # Fallback for GET request
    return render_template("/show/search_multiple_panelists.html",
                           panelists=panelists,
                           shows=None)

#endregion

#region Application Initialization
config = load_config()
app_time_zone = config["settings"]["app_time_zone"]
time_zone_name = config["settings"]["time_zone"]
app.jinja_env.globals["app_version"] = APP_VERSION
app.jinja_env.globals["ga_property_code"] = config["settings"]["ga_property_code"]
app.jinja_env.globals["time_zone"] = app_time_zone
app.jinja_env.globals["rendered_at"] = utility.generate_date_time_stamp
app.jinja_env.globals["current_year"] = utility.current_year

app.jinja_env.globals["site_url"] = config["settings"]["site_url"]
app.jinja_env.globals["stats_url"] = config["settings"]["stats_url"]
database_connection = mysql.connector.connect(**config["database"])
database_connection.autocommit = True

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port="9248")

#endregion
