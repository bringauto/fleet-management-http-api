#!/usr/bin/env python3

import connexion
import asyncio

from openapi_server import encoder
from openapi_server.database.database_async import AsyncDatabase

async def init_db():
    db = AsyncDatabase.get_instance()
    #result = await db.fetchone("SELECT pg_sleep(3); SELECT 42;")
    #print(result)

def main():
    asyncio.run(init_db())
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'BringAuto Fleet Management API'},
                pythonic_params=True)

    app.run(port=8080)


if __name__ == '__main__':
    main()
