#!/usr/bin/env python3

import connexion
import os
import psycopg2

from openapi_server import encoder
from dotenv import load_dotenv


def main():
    load_dotenv()
    db_url = os.environ.get("DATABASE_URL")
    db_name = os.environ.get("DATABASE_NAME")
    db_user = os.environ.get("DATABASE_USER")
    db_password = os.environ.get("DATABASE_PASSWORD")
    connection = psycopg2.connect(host=db_url, dbname=db_name, user=db_user, password=db_password)
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'BringAuto Fleet Management API'},
                pythonic_params=True)

    app.run(port=8080)


if __name__ == '__main__':
    main()
