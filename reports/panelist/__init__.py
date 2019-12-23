# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""Explicitly listing all panelist reporting modules"""

from reports.panelist import (aggregate_scores, appearances_by_year,
                              gender_mix, gender_stats, panelist_vs_panelist,
                              win_streaks)

__all__ = [
    "aggregate_scores",
    "appearances_by_year",
    "gender_mix",
    "gender_stats",
    "panelist_vs_panelist",
    "win_streaks"
    ]
