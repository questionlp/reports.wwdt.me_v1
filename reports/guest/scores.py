# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""WWDTM Guest Scores Report Functions"""

from collections import OrderedDict
from typing import List, Dict
import mysql.connector
from mysql.connector import DatabaseError, ProgrammingError

#region Retrieval Functions
def retrieve_guest_scoring_exceptions(guest_id: int,
                                      database_connection: mysql.connector.connect
                                     ) -> List[Dict]:
    """Retrieve a list of instances where a requested Not My Job guest
    has had a scoring exception"""

    exceptions = []
    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT g.guestid, g.guest, s.showid, s.showdate, "
             "gm.guestscore, gm.exception, sn.shownotes "
             "FROM ww_showguestmap gm "
             "JOIN ww_shows s ON s.showid = gm.showid "
             "JOIN ww_guests g ON g.guestid = gm.guestid "
             "JOIN ww_shownotes sn on sn.showid = gm.showid "
             "WHERE g.guestid = %s "
             "AND s.bestof = 0 AND s.repeatshowid IS NULL "
             "AND gm.exception = 1 "
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
        show["score"] = row["guestscore"]
        show["exception"] = bool(row["exception"])
        show["notes"] = row["shownotes"]
        exceptions.append(show)

    return exceptions

def retrieve_guest_scores(guest_id: int,
                          database_connection: mysql.connector.connect
                         ) -> List[Dict]:
    """Retrieve a list of instances where a requested Not My Job guest
    has received three points"""

    scores = []
    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT g.guestid, g.guest, s.showid, s.showdate, "
             "gm.guestscore, gm.exception, sn.shownotes "
             "FROM ww_showguestmap gm "
             "JOIN ww_shows s ON s.showid = gm.showid "
             "JOIN ww_guests g ON g.guestid = gm.guestid "
             "JOIN ww_shownotes sn on sn.showid = gm.showid "
             "WHERE g.guestid = %s "
             "AND s.bestof = 0 AND s.repeatshowid IS NULL "
             "AND gm.exception = 1 "
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
        show["score"] = row["guestscore"]
        show["exception"] = bool(row["exception"])
        show["notes"] = row["shownotes"]
        scores.append(show)

    return scores


def retrieve_all_scoring_exceptions(database_connection: mysql.connector.connect
                                   ) -> List[Dict]:
    """Retrieve a list of all Not My Job scoring exceptions"""

    exceptions = []

    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT DISTINCT g.guestid, g.guest, g.guestslug "
             "FROM ww_showguestmap gm "
             "JOIN ww_shows s ON s.showid = gm.showid "
             "JOIN ww_guests g ON g.guestid = gm.guestid "
             "WHERE s.bestof = 0 AND s.repeatshowid IS NULL "
             "AND gm.exception = 1 "
             "ORDER BY g.guest ASC;")
    cursor.execute(query)
    result = cursor.fetchall()

    if not result:
        return None

    for row in result:
        guest = OrderedDict()
        guest["id"] = row["guestid"]
        guest["name"] = row["guest"]
        guest["slug"] = row["guestslug"]
        guest["exceptions"] = retrieve_guest_scoring_exceptions(guest_id=guest["id"],
                                                                database_connection=database_connection)
        exceptions.append(guest)

    return exceptions

def retrieve_all_three_pointers(database_connection: mysql.connector.connect
                                ) -> List[Dict]:
    """Retrieve a list instances where Not My Job guests have answered
    all three questions correctly or received all three points"""

    three_pointers = []

    cursor = database_connection.cursor(dictionary=True)
    query = ("(SELECT g.guestid, g.guest, g.guestslug, s.showid, s.showdate, "
             " gm.guestscore, gm.exception, sn.shownotes "
             " FROM ww_showguestmap gm "
             " JOIN ww_shows s ON s.showid = gm.showid "
             " JOIN ww_guests g ON g.guestid = gm.guestid "
             " JOIN ww_shownotes sn ON sn.showid = gm.showid "
             " WHERE s.bestof = 0 AND s.repeatshowid IS NULL "
             " AND gm.guestscore = 3 "
             ") "
             "UNION "
             "(SELECT g.guestid, g.guest, g.guestslug, s.showid, s.showdate, "
             " gm.guestscore, gm.exception, sn.shownotes "
             " FROM ww_showguestmap gm "
             " JOIN ww_shows s ON s.showid = gm.showid "
             " JOIN ww_guests g ON g.guestid = gm.guestid "
             " JOIN ww_shownotes sn ON sn.showid = gm.showid "
             " WHERE s.bestof = 1 AND s.repeatshowid IS NULL "
             " AND gm.guestscore = 3 "
             " AND g.guestid NOT IN ( "
	         " SELECT gm.guestid "
	         " FROM ww_showguestmap gm "
	         " JOIN ww_shows s ON s.showid = gm.showid "
	         " WHERE s.bestof = 0 AND s.repeatshowid IS NULL "
             " ) "
             ")"
             "ORDER BY guest ASC, showdate ASC;")
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
        guest["show_date"] = row["showdate"].isoformat()
        guest["score"] = row["guestscore"]
        guest["exception"] = bool(row["exception"])
        guest["show_notes"] = row["shownotes"]
        three_pointers.append(guest)

    return three_pointers

#endregion
