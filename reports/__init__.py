# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""Explicitly listing all reporting modules"""

from reports.guest import best_of_only, scores
from reports.location import average_scores
from reports.panelist import (aggregate_scores, appearances_by_year,
                              gender_mix, gender_stats, panelist_vs_panelist,
                              stats_summary, win_streaks)
from reports.scorekeeper import introductions
from reports.show import lightning_round, show_details

__all__ = [
    "guest",
    "location",
    "panelist",
    "scorekeeper",
    "show"
]
