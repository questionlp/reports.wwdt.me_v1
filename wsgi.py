# -*- coding: utf-8 -*-
# Copyright (c) 2018-2022 Linh Pham
# reports.wwdt.me is released under the terms of the Apache License 2.0
"""Flask WSGI startup file"""

from app import app

if __name__ == "__main__":
    app.run(debug=False)
