# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""WWDTM Search Shows by Multiple Selected Panelists Report Functions"""

from collections import OrderedDict
from typing import Dict, List, Optional
import mysql.connector

from . import show_details as details

#region Retrieval Functions
def retrieve_panelist_slugs(database_connection: mysql.connector.connect
                           ) -> List[str]:
    """Returns a list of valid panelist slugs"""
    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT panelistslug FROM ww_panelists "
             "WHERE panelistslug <> 'multiple' "
             "ORDER BY panelist ASC;")
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return None

    panelist_slugs = []
    for row in result:
        panelist_slugs.append(row["panelistslug"])

    return panelist_slugs

def retrieve_panelists(database_connection: mysql.connector.connect
                      ) -> Dict:
    """Returns a dictionary containing valid panelists"""
    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT panelistslug, panelist FROM ww_panelists "
             "WHERE panelistslug <> 'multiple' "
             "ORDER BY panelist ASC;")
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return None

    panelists = OrderedDict()
    for row in result:
        panelists[row["panelistslug"]] = row["panelist"]

    return panelists

def retrieve_details(show_id: int,
                     database_connection: mysql.connector.connect
                    ) -> List[Dict]:
    """Retrieve show details for the requested show ID"""

    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT s.showid, s.showdate, s.bestof, s.repeatshowid, l.venue, "
             "l.city, l.state, h.host, sk.scorekeeper "
             "FROM ww_shows s "
             "JOIN ww_showlocationmap lm ON lm.showid = s.showid "
             "JOIN ww_locations l on l.locationid = lm.locationid "
             "JOIN ww_showhostmap hm ON hm.showid = s.showid "
             "JOIN ww_hosts h on h.hostid = hm.hostid "
             "JOIN ww_showskmap skm ON skm.showid = s.showid "
             "JOIN ww_scorekeepers sk ON sk.scorekeeperid = skm.scorekeeperid "
             "WHERE s.showid = %s;")
    cursor.execute(query, (show_id, ))
    result = cursor.fetchone()
    cursor.close()

    if not result:
        return None

    show = OrderedDict()
    show["id"] = result["showid"]
    show["date"] = result["showdate"].isoformat()
    show["best_of"] = bool(result["bestof"])
    show["repeat"] = bool(result["repeatshowid"])
    show["location"] = OrderedDict()
    show["location"]["venue"] = result["venue"]
    show["location"]["city"] = result["city"]
    show["location"]["state"] = result["state"]
    show["host"] = result["host"]
    show["scorekeeper"] = result["scorekeeper"]
    show["panelists"] = details.retrieve_show_panelists(show_id=show["id"],
                                                        database_connection=database_connection)
    show["guests"] = details.retrieve_show_guests(show_id=show["id"],
                                                  database_connection=database_connection)

    return show

def retrieve_matching_one(database_connection: mysql.connector.connect,
                          panelist_slug_1: str,
                          include_best_of: Optional[bool] = False,
                          include_repeats: Optional[bool] = False
                         ) -> List[Dict]:
    """Retrieve show details for shows with a panel containing one of
    the requested panelists"""

    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT s.showid, s.bestof, s.repeatshowid "
             "FROM ww_showpnlmap pm "
             "JOIN ww_shows s ON s.showid = pm.showid "
             "JOIN ww_panelists p ON p.panelistid = pm.panelistid "
             "WHERE p.panelistslug = %s "
             "GROUP BY s.showid "
             "HAVING COUNT(s.showid) = 1 "
             "ORDER BY s.showdate ASC;")
    cursor.execute(query, (panelist_slug_1, ))
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return None

    shows = []
    for row in result:
        best_of = bool(row["bestof"])
        repeat = bool(row["repeatshowid"])

        if (best_of and repeat) and (include_best_of or include_repeats):
            shows.append(retrieve_details(row["showid"], database_connection))

        if (best_of and not include_best_of) or (repeat and not include_repeats):
            continue

        shows.append(retrieve_details(row["showid"], database_connection))

    return shows

def retrieve_matching_two(database_connection: mysql.connector.connect,
                          panelist_slug_1: str,
                          panelist_slug_2: str,
                          include_best_of: Optional[bool] = False,
                          include_repeats: Optional[bool] = False
                         ) -> List[Dict]:
    """Retrieve show details for shows with a panel containing two of
    the requested panelists"""

    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT s.showid, s.bestof, s.repeatshowid "
             "FROM ww_showpnlmap pm "
             "JOIN ww_shows s ON s.showid = pm.showid "
             "JOIN ww_panelists p ON p.panelistid = pm.panelistid "
             "WHERE p.panelistslug IN (%s, %s) "
             "GROUP BY s.showid "
             "HAVING COUNT(s.showid) = 2 "
             "ORDER BY s.showdate ASC;")
    cursor.execute(query, (panelist_slug_1,
                           panelist_slug_2, ))
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return None

    shows = []
    for row in result:
        best_of = bool(row["bestof"])
        repeat = bool(row["repeatshowid"])

        if (best_of and repeat) and (include_best_of or include_repeats):
            shows.append(retrieve_details(row["showid"], database_connection))

        if (best_of and not include_best_of) or (repeat and not include_repeats):
            continue

        shows.append(retrieve_details(row["showid"], database_connection))

    return shows

def retrieve_matching_three(database_connection: mysql.connector.connect,
                            panelist_slug_1: str,
                            panelist_slug_2: str,
                            panelist_slug_3: str,
                            include_best_of: Optional[bool] = False,
                            include_repeats: Optional[bool] = False
                           ) -> List[Dict]:
    """Retrieve show details for shows with a panel containing three of
    the requested panelists"""

    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT s.showid, s.bestof, s.repeatshowid "
             "FROM ww_showpnlmap pm "
             "JOIN ww_shows s ON s.showid = pm.showid "
             "JOIN ww_panelists p ON p.panelistid = pm.panelistid "
             "WHERE p.panelistslug IN (%s, %s, %s) "
             "GROUP BY s.showid "
             "HAVING COUNT(s.showid) = 3 "
             "ORDER BY s.showdate ASC;")
    cursor.execute(query, (panelist_slug_1,
                           panelist_slug_2,
                           panelist_slug_3, ))
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return None

    shows = []
    for row in result:
        best_of = bool(row["bestof"])
        repeat = bool(row["repeatshowid"])

        if (best_of and repeat) and (include_best_of or include_repeats):
            shows.append(retrieve_details(row["showid"], database_connection))

        if (best_of and not include_best_of) or (repeat and not include_repeats):
            continue

        shows.append(retrieve_details(row["showid"], database_connection))

    return shows



#endregion
