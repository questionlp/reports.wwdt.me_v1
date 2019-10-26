# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""WWDTM Panelist vs Panelist Report Functions"""

from collections import OrderedDict
from typing import List, Dict, Text
import mysql.connector
import slugify

#region Retrieval Functions
def retrieve_panelists(database_connection: mysql.connector.connect
                      ) -> List[Dict]:
    """Retrieve panelists from the Stats Page database"""

    panelists = []
    try:
        cursor = database_connection.cursor()
        query = ("SELECT DISTINCT p.panelistid, p.panelist, p.panelistslug "
                 "FROM ww_showpnlmap pm "
                 "JOIN ww_panelists p ON p.panelistid = pm.panelistid "
                 "WHERE pm.panelistscore IS NOT NULL "
                 "AND p.panelist <> '<Multiple>' "
                 "ORDER BY p.panelist ASC;")
        cursor.execute(query, )
        result = cursor.fetchall()
        cursor.close()

        for panelist in result:
            panelist_info = OrderedDict()
            panelist_info["id"] = panelist[0]
            panelist_info["name"] = panelist[1]
            panelist_info["slug"] = panelist[2]
            panelists.append(panelist_info)

        return panelists
    except mysql.connector.Error:
        return

def retrieve_panelist_appearances(panelists: List[Dict],
                                  database_connection: mysql.connector.connect
                                 ) -> Dict:
    """Retrieve panelist appearances from the Stats Page database"""

    panelist_appearances = OrderedDict()
    for panelist in panelists:
        try:
            appearances = []
            cursor = database_connection.cursor()
            query = ("SELECT s.showdate FROM ww_showpnlmap pm "
                     "JOIN ww_panelists p ON p.panelistid = pm.panelistid "
                     "JOIN ww_shows s ON s.showid = pm.showid "
                     "WHERE p.panelistid = %s "
                     "AND pm.panelistscore IS NOT NULL "
                     "AND s.bestof = 0 "
                     "AND s.repeatshowid IS NULL "
                     "ORDER BY s.showdate ASC;")
            cursor.execute(query, (panelist["id"],))
            result = cursor.fetchall()
            cursor.close()

            if result:
                for appearance in result:
                    appearances.append(appearance[0].isoformat())

                panelist_appearances[panelist["id"]] = appearances
        except mysql.connector.Error:
            return

    return panelist_appearances

def retrieve_show_scores(database_connection: mysql.connector.connect) -> Dict:
    """Retrieve scores for each show and panelist from the Stats Page Database"""

    shows = OrderedDict()

    try:
        cursor = database_connection.cursor()
        query = ("SELECT s.showdate, p.panelistid, pm.panelistscore FROM ww_showpnlmap pm "
                 "JOIN ww_panelists p ON p.panelistid = pm.panelistid "
                 "JOIN ww_shows s ON s.showid = pm.showid "
                 "WHERE s.bestof = 0 "
                 "AND s.repeatshowid IS NULL "
                 "AND pm.panelistscore IS NOT NULL "
                 "ORDER BY s.showdate ASC, pm.panelistscore DESC;")
        cursor.execute(query, )
        result = cursor.fetchall()
        cursor.close()

        if result:
            for show in result:
                show_date = show[0].isoformat()
                if show_date not in shows:
                    shows[show_date] = OrderedDict()

                panelist_id = show[1]
                panelist_score = show[2]
                shows[show_date][panelist_id] = panelist_score

        return shows
    except mysql.connector.Error:
        return

def generate_panelist_vs_panelist_results(panelists: List[Dict],
                                          panelist_appearances: Dict,
                                          show_scores: Dict
                                          ) -> Dict:
    """Generate panelist vs panelist results"""

    pvp_results = OrderedDict()
    for panelist_a in panelists:
        panelist_a_id = panelist_a["id"]
        pvp_results[panelist_a_id] = OrderedDict()
        for panelist_b in panelists:
            panelist_b_id = panelist_b["id"]
            if panelist_a_id != panelist_b_id:
                panelist_a_appearances = panelist_appearances[panelist_a_id]
                panelist_b_appearances = panelist_appearances[panelist_b_id]
                a_b_intersect = list(set(panelist_a_appearances) & set(panelist_b_appearances))
                a_b_intersect.sort()

                pvp_results[panelist_a_id][panelist_b_id] = OrderedDict()
                wins = 0
                draws = 0
                losses = 0
                for show in a_b_intersect:
                    panelist_a_score = show_scores[show][panelist_a_id]
                    panelist_b_score = show_scores[show][panelist_b_id]
                    if panelist_a_score > panelist_b_score:
                        wins = wins + 1
                    elif panelist_a_score == panelist_b_score:
                        draws = draws + 1
                    else:
                        losses = losses + 1

                pvp_results[panelist_a_id][panelist_b_id]["wins"] = wins
                pvp_results[panelist_a_id][panelist_b_id]["draws"] = draws
                pvp_results[panelist_a_id][panelist_b_id]["losses"] = losses

    return pvp_results

#endregion