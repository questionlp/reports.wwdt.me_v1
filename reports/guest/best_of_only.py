# -*- coding: utf-8 -*-
# Copyright (c) 2018-2022 Linh Pham
# reports.wwdt.me is released under the terms of the Apache License 2.0
"""WWDTM Guest Best Of Only Appearances Report Functions"""

from collections import OrderedDict
from typing import List, Dict
import mysql.connector

#region Retrieval Functions
def retrieve_guest_appearances(guest_id: int,
                               database_connection: mysql.connector.connect
                              ) -> List[Dict]:
    """Retrieve a list of shows in which the requested Not My Job guest
    has made an appearance on (including Best Of and Repeats)"""

    shows = []
    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT s.showid, s.showdate, s.bestof, s.repeatshowid, "
             "gm.guestscore, gm.exception "
             "FROM ww_showguestmap gm "
             "JOIN ww_shows s ON s.showid = gm.showid "
             "JOIN ww_guests g ON g.guestid = gm.guestid "
             "WHERE g.guestid = %s "
             "ORDER BY s.showdate ASC;")
    cursor.execute(query, (guest_id,))
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return None

    for row in result:
        show = OrderedDict()
        show["id"] = row["showid"]
        show["date"] = row["showdate"].isoformat()
        show["best_of"] = bool(row["bestof"])
        show["repeat_show"] = bool(row["repeatshowid"])
        show["score"] = row["guestscore"]
        show["exception"] = bool(row["exception"])
        shows.append(show)

    return shows

def retrieve_best_of_only_guests(database_connection: mysql.connector.connect
                                ) -> List[Dict]:
    """Retrieves a list of Not My Job guests that have only appeared
    on Best Of shows"""

    guests = []

    # Retrieve a list of guest IDs that only have appearances on shows
    # flagged as Best Of shows
    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT DISTINCT g.guestid, g.guest, g.guestslug "
             "FROM ww_showguestmap gm "
             "JOIN ww_shows s ON s.showid = gm.showid "
             "JOIN ww_guests g ON g.guestid = gm.guestid "
             "WHERE s.bestof = 1 AND s.repeatshowid IS NULL "
             "AND g.guestid NOT IN ( "
	         "  SELECT gm.guestid "
	         "  FROM ww_showguestmap gm "
	         "  JOIN ww_shows s ON s.showid = gm.showid "
	         "  WHERE s.bestof = 0 AND s.repeatshowid IS NULL )"
            )
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return None

    for row in result:
        guest = OrderedDict()
        guest["id"] = row["guestid"]
        guest["name"] = row["guest"]
        guest["slug"] = row["guestslug"]
        guest["appearances"] = retrieve_guest_appearances(guest_id=guest["id"],
                                                          database_connection=database_connection)
        guests.append(guest)

    return guests

#endregion
