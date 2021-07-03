# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""Explicitly listing all reporting modules"""

from reports.guest import (best_of_only,
                           most_appearances,
                           scores)
from reports.location import average_scores
from reports.panelist import (aggregate_scores,
                              appearances as panelist_appearances,
                              appearances_by_year,
                              bluff_stats,
                              gender_mix,
                              gender_stats,
                              panelist_vs_panelist_scoring,
                              panelist_vs_panelist,
                              rankings_summary,
                              single_appearance,
                              stats_summary,
                              streaks)
from reports.scorekeeper import (appearances as scorekeeper_appearances,
                                 introductions)
from reports.show import (all_women_panel,
                          guest_hosts,
                          guest_scorekeeper,
                          lightning_round,
                          scoring,
                          search_multiple_panelists,
                          show_counts,
                          show_details)

__all__ = [
    "guest",
    "location",
    "panelist",
    "scorekeeper",
    "show"
]
