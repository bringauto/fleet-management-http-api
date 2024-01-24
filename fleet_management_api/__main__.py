#!/usr/bin/env python3
from typing import Dict
import json

import fleet_management_api.app as app
from fleet_management_api.database import set_up_database, set_content_timeout, content_timeout


def main():
    application = app.get_app()
    config = _load_config()
    db_config = config["database"]
    set_up_database(db_config)
    application.run(port=8080)


def _load_config() -> Dict:
    fp = open("./config/config.json", "r")
    return json.load(fp)


if __name__ == '__main__':
    main()
