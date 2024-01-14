import aiomysql
from loader import loop
import os
from dotenv import load_dotenv


load_dotenv()

async def connect():
    return await aiomysql.create_pool(
        host = os.getenv('DB_HOST'),
        port = int(os.getenv('DB_PORT')),
        user = os.getenv('DB_LOGIN'),
        password = os.getenv('DB_PASSWORD'),
        db = os.getenv('DB_TABLE'),
        autocommit = True,
        pool_recycle = 100,
        loop = loop
    )

db_connect = loop.run_until_complete(connect())
