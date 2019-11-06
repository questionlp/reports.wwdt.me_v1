# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""WWDTM Lightning Round Report Functions"""

from collections import OrderedDict
from typing import List, Dict
import mysql.connector
from mysql.connector import DatabaseError, ProgrammingError

#region Retrieval Functions
def retrieve_all_lightning_round_start(database_connection: mysql.connector.connect
                                      ) -> Dict:
    """Retrieve all Lightning Fill-in-the-Blank round starting scores
    and return the values as an OrderedDict"""

    show_lightning_round_starts = OrderedDict()
    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT s.showid, s.showdate, p.panelistid, p.panelist, "
             "pm.panelistlrndstart "
             "FROM ww_showpnlmap pm "
             "JOIN ww_shows s ON s.showid = pm.showid "
             "JOIN ww_panelists p ON p.panelistid = pm.panelistid "
             "WHERE s.bestof = 0 AND s.repeatshowid IS NULL "
             "AND s.showdate <> '2018-10-27' " # Excluding 25th anniversary special
             "AND pm.panelistlrndstart IS NOT NULL "
             "ORDER BY s.showdate ASC;")
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return None

    for row in result:
        show_id = row["showid"]
        if show_id not in show_lightning_round_starts:
            show_lightning_round_starts[show_id] = OrderedDict()
            show_lightning_round_starts[show_id]["id"] = show_id
            show_lightning_round_starts[show_id]["date"] = row["showdate"].isoformat()
            show_lightning_round_starts[show_id]["scores"] = []

        show_lightning_round_starts[show_id]["scores"].append(row["panelistlrndstart"])

    return show_lightning_round_starts

def retrieve_panelists_by_show_id(show_id: int,
                                  database_connection: mysql.connector.connect
                                  ) -> List[Dict]:
    """Returns a list of panelists for the requested show ID"""

    panelists = []
    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT p.panelistid, p.panelist, p.panelistslug "
             "FROM ww_showpnlmap pm "
             "JOIN ww_panelists p ON p.panelistid = pm.panelistid "
             "JOIN ww_shows s ON s.showid = pm.showid "
             "WHERE s.showid = %s "
             "ORDER BY pm.showpnlmapid ASC;")
    cursor.execute(query, (show_id,))
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return None

    for row in result:
        panelist = OrderedDict()
        panelist["id"] = row["panelistid"]
        panelist["name"] = row["panelist"]
        panelist["slug"] = row["panelistslug"]
        panelists.append(panelist)

    return panelists

def shows_with_same_lightning_round_start(database_connection: mysql.connector.connect
                                         ) -> Dict:
    """Return shows in which the Lightning Fill-in-the-Blank round
    started with the same score for all three panelists"""

    show_scores = retrieve_all_lightning_round_start(database_connection)
    shows = OrderedDict()

    for show in show_scores:
        show_id = show_scores[show]["id"]
        show_date = show_scores[show]["date"]

        if len(set(show_scores[show]["scores"])) == 1:
            print(show_scores[show])
            shows[show_date] = OrderedDict()
            shows[show_date]["id"] = show_id
            shows[show_date]["date"] = show_date
            shows[show_date]["score"] = show_scores[show]["scores"][0]
            shows[show_date]["panelists"] = retrieve_panelists_by_show_id(show_id=show_id,
                                                                          database_connection=database_connection)

    return shows

#endregion
