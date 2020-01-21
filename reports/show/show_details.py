# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""WWDTM Show Details Report Functions"""

from collections import OrderedDict
from typing import List, Dict
import mysql.connector

#region Retrieval Functions
def retrieve_show_guests(show_id: int,
                         database_connection: mysql.connector.connect
                        ) -> List[Dict]:
    """Retrieve the Not My Job guest for the requested show ID"""

    guests = []
    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT g.guestid, g.guest, g.guestslug "
             "FROM ww_showguestmap gm "
             "JOIN ww_guests g on g.guestid = gm.guestid "
             "WHERE gm.showid = %s;")
    cursor.execute(query, (show_id, ))
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return None

    for row in result:
        guest = OrderedDict()
        guest["id"] = row["guestid"]
        guest["name"] = row["guest"]
        guest["slug"] = row["guestslug"]
        guests.append(guest)

    return guests

def retrieve_show_panelists(show_id: int,
                            database_connection: mysql.connector.connect
                           ) -> List[Dict]:
    """Retrieve panelists for the requested show ID"""

    panelists = []
    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT p.panelistid, p.panelist, p.panelistslug "
             "FROM ww_showpnlmap pm "
             "JOIN ww_panelists p ON p.panelistid = pm.panelistid "
             "WHERE pm.showid = %s "
             "ORDER BY pm.showpnlmapid ASC;")
    cursor.execute(query, (show_id, ))
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

def retrieve_all_shows(database_connection: mysql.connector.connect
                      ) -> List[Dict]:
    """Retrieve a list of all shows and basic information including:
    location, host, scorekeeper, panelists and guest"""

    shows = []
    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT s.showid, s.showdate, s.bestof, s.repeatshowid, "
             "l.venue, l.city, l.state, h.host, sk.scorekeeper "
             "FROM ww_shows s "
             "JOIN ww_showlocationmap lm ON lm.showid = s.showid "
             "JOIN ww_locations l on l.locationid = lm.locationid "
             "JOIN ww_showhostmap hm ON hm.showid = s.showid "
             "JOIN ww_hosts h on h.hostid = hm.hostid "
             "JOIN ww_showskmap skm ON skm.showid = s.showid "
             "JOIN ww_scorekeepers sk ON sk.scorekeeperid = skm.scorekeeperid "
             "AND s.showdate < NOW() "
             "ORDER BY s.showdate ASC;")
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return None

    show_count = 1
    for row in result:
        show = OrderedDict()
        show["count"] = show_count
        show["id"] = row["showid"]
        show["date"] = row["showdate"]
        show["best_of"] = bool(row["bestof"])
        show["repeat"] = bool(row["repeatshowid"])
        show["location"] = OrderedDict()
        show["location"]["venue"] = row["venue"]
        show["location"]["city"] = row["city"]
        show["location"]["state"] = row["state"]
        show["host"] = row["host"]
        show["scorekeeper"] = row["scorekeeper"]
        show["guests"] = retrieve_show_guests(show_id=show["id"],
                                              database_connection=database_connection)
        show["panelists"] = retrieve_show_panelists(show_id=show["id"],
                                                    database_connection=database_connection)
        shows.append(show)
        show_count += 1

    return shows

def retrieve_all_original_shows(database_connection: mysql.connector.connect
                               ) -> List[Dict]:
    """Retrieve a list of all original shows and basic information
    including: location, host, scorekeeper, panelists and guest"""

    shows = []
    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT s.showid, s.showdate, l.venue, l.city, l.state, "
             "h.host, sk.scorekeeper "
             "FROM ww_shows s "
             "JOIN ww_showlocationmap lm ON lm.showid = s.showid "
             "JOIN ww_locations l on l.locationid = lm.locationid "
             "JOIN ww_showhostmap hm ON hm.showid = s.showid "
             "JOIN ww_hosts h on h.hostid = hm.hostid "
             "JOIN ww_showskmap skm ON skm.showid = s.showid "
             "JOIN ww_scorekeepers sk ON sk.scorekeeperid = skm.scorekeeperid "
             "WHERE s.bestof = 0 AND s.repeatshowid IS NULL "
             "AND s.showdate < NOW() "
             "ORDER BY s.showdate ASC;")
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return None

    show_count = 1
    for row in result:
        show = OrderedDict()
        show["count"] = show_count
        show["id"] = row["showid"]
        show["date"] = row["showdate"]
        show["location"] = OrderedDict()
        show["location"]["venue"] = row["venue"]
        show["location"]["city"] = row["city"]
        show["location"]["state"] = row["state"]
        show["host"] = row["host"]
        show["scorekeeper"] = row["scorekeeper"]
        show["guest"] = retrieve_show_guests(show_id=show["id"],
                                             database_connection=database_connection)
        show["panelists"] = retrieve_show_panelists(show_id=show["id"],
                                                    database_connection=database_connection)
        shows.append(show)
        show_count += 1

    return shows

#endregion
