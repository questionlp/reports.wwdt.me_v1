# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Linh Pham
# reports.wwdt.me is relased under the terms of the Apache License 2.0
"""Flask application startup file"""

import os

import mysql.connector
from mysql.connector.errors import DatabaseError, ProgrammingError
from flask import Flask, abort, make_response, request

app = Flask(__name__)
app.url_map.strict_slashes = False

#region Bootstrap Functions
def load_config():
    """Bootstrap the API by loading in configuration and initializing
    Flask app"""
    app_environment = os.getenv("API_ENV", "local").strip().lower()

    try:
        with open('config.json', 'r') as config_file:
            config_dict = json.load(config_file)
    except FileNotFoundError as err:
        raise FileNotFoundError("Unable to locate config.json") from err
    except IOError as err:
        raise IOError("Unable to read config.json") from err

    if app_environment.startswith("develop"):
        if "development" in config_dict:
            return config_dict["development"]
        else:
            raise EnvironmentError("Missing 'development' section in config file")
    elif app_environment.startswith("prod"):
        if "production" in config_dict:
            return config_dict["production"]
        else:
            raise EnvironmentError("Missing 'production' section in config file")
    else:
        if "local" in config_dict:
            return config_dict["local"]
        else:
            raise EnvironmentError("Missing 'local' section in config file")

#endregion



#region Application Initialization
config_dict = load_config()
database_connection = mysql.connector.connect(**config_dict["database"])
database_connection.autocommit = True

if __name__ == '__main__':    
    app.run(debug=False, host="0.0.0.0", port="9248")

#endregion