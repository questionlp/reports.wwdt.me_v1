# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""WWDTM Location Score Breakdown Report Functions"""

from collections import OrderedDict
from typing import List, Dict
import mysql.connector
from mysql.connector import DatabaseError, ProgrammingError
import numpy

#region Retrieval Functions
def retrieve_average_scores_by_location(database_connection: mysql.connector.connect
                                       ) -> List[Dict]:
    """Retrieve average scores sorted by location using a pre-written
    database query"""

    average_scores = []
    cursor = database_connection.cursor(dictionary=True)
    # Excluding 25th Anniversary Show at Chicago Theatre from calculations
    # due to non-standard number of panelist scores and score totals
    query = ("SELECT l.locationid, l.venue, l.city, l.state, "
             "SUM(pm.panelistscore) / (COUNT(s.showid) / 3) AS average, "
             "COUNT(s.showid) / 3 AS shows "
             "FROM ww_showpnlmap pm "
             "JOIN ww_shows s ON s.showid = pm.showid "
             "join ww_showlocationmap lm ON lm.showid = pm.showid "
             "JOIN ww_locations l ON l.locationid = lm.locationid "
             "WHERE s.bestof = 0 AND s.repeatshowid IS NULL "
             "AND s.showdate <> '2018-10-27' "
             "GROUP BY l.locationid "
             "ORDER BY average DESC")
    cursor.execute(query)
    result = cursor.fetchall()

    if not result:
        return None

    for row in result:
        location = OrderedDict()
        location["id"] = row["locationid"]
        location["venue"] = row["venue"]
        location["city"] = row["city"]
        location["state"] = row["state"]
        location["average"] = row["average"]
        location["show_count"] = row["shows"]
        average_scores.append(location)

    return average_scores

#endregion
