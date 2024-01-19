#!/usr/bin/env python3

import fleet_management_api.app as app
from fleet_management_api.database.connection import set_test_connection_source, current_connection_source, Base


def main():
    set_test_connection_source("fleet_management.db")
    Base.metadata.create_all(bind=current_connection_source())
    application = app.get_app()
    application.run(port=8080)


if __name__ == '__main__':
    main()
