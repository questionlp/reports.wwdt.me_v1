# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""Explicitly listing all panelist reporting modules"""

from reports.panelist import (aggregate_scores,
                              appearances,
                              appearances_by_year,
                              bluff_stats,
                              debut_by_year,
                              gender_mix,
                              gender_stats,
                              panelist_vs_panelist,
                              panelist_vs_panelist_scoring,
                              rankings_summary,
                              single_appearance,
                              stats_summary, streaks)

__all__ = [
    "aggregate_scores",
    "appearances",
    "appearances_by_year",
    "bluff_stats",
    "debut_by_year",
    "gender_mix",
    "gender_stats",
    "panelist_vs_panelist",
    "panelist_vs_panelist_scoring",
    "rankings_summary",
    "single_appearance",
    "stats_summary",
    "streaks"
    ]
