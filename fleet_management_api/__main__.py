#!/usr/bin/env python3
from typing import Dict
import json

import fleet_management_api.app as app
from fleet_management_api.database import set_connection_source, set_up_database


def main():
    set_connection_source("localhost:5432", "fleet_management", "postgres", "1234")
    application = app.get_app()
    config = _load_config()
    set_up_database(config["database"])
    application.run(port=8080)


def _load_config() -> Dict:
    fp = open("./config/config.json", "r")
    return json.load(fp)


if __name__ == '__main__':
    main()
