#!/usr/bin/env python3

import fleet_management_api.app as app


def main():
    application = app.get_app()
    application.run(port=8080)


if __name__ == '__main__':
    main()
