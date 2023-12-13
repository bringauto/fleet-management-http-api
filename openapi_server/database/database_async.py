import asyncio
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

class AsyncDatabase:
    _instance = None

    @staticmethod
    def get_instance():
        if AsyncDatabase._instance is None:
            load_dotenv()
            db_url = os.environ.get("DATABASE_URL")
            db_name = os.environ.get("DATABASE_NAME")
            db_user = os.environ.get("DATABASE_USER")
            db_password = os.environ.get("DATABASE_PASSWORD")
            AsyncDatabase(host=db_url, dbname=db_name, user=db_user, password=db_password)
            AsyncDatabase._instance.connect()
        return AsyncDatabase._instance

    def __init__(self, host, dbname, user, password):
        if AsyncDatabase._instance is not None:
            raise Exception("Database already initialized")
        else:
            AsyncDatabase._instance = self

        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        self.connection = psycopg2.connect(host=self.host, dbname=self.dbname, user=self.user, password=self.password)

    async def execute(self, query):
        loop = asyncio.get_event_loop()
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            result = await loop.run_in_executor(None, cursor.execute, query)
            return result

    async def fetchall(self, query):
        loop = asyncio.get_event_loop()
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            await loop.run_in_executor(None, cursor.execute, query)
            result = await loop.run_in_executor(None, cursor.fetchall)
            return result

    async def fetchone(self, query):
        loop = asyncio.get_event_loop()
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            await loop.run_in_executor(None, cursor.execute, query)
            result = await loop.run_in_executor(None, cursor.fetchone)
            return result