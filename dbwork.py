from aiomysql import Pool, DictCursor
import pymysql
from connect import db_connect


class DBCommands:
  pool: Pool = db_connect


  async def add_user(self,chat_id,username):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("INSERT INTO users (chat_id,username) VALUES (%s,%s)",(chat_id,username))
        return await cur.fetchone()


  async def upd_user(self,status,username):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("UPDATE users SET status=%s WHERE username=%s",(status,username))


  async def get_user(self,username):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("SELECT * from users WHERE username=%s",(username))
        return await cur.fetchone()


  async def del_user(self,username):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("DELETE FROM users WHERE username=%s",(username))


  async def get_admin(self):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("SELECT * from users WHERE username='agressor73732'")
        return await cur.fetchone()


  async def get_ready(self):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("SELECT * from users WHERE is_ready=1 AND role='user' AND status='approved'")
        return await cur.fetchall()


  async def get_not_ready(self):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("SELECT * from users WHERE is_ready=0 AND role='user' AND status='approved'")
        return await cur.fetchall()


  async def upd_user_ready(self,chat_id):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("UPDATE users SET is_ready=1 WHERE chat_id=%s",(chat_id))


  async def clear_user_ready(self):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("UPDATE users SET is_ready=0 WHERE is_ready=1 AND role='user' AND status='approved'")


  async def get_all_users(self):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("SELECT * from users WHERE role='user'")
        return await cur.fetchall()


  async def  get_all_approved_users(self):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("SELECT * from users WHERE role='user' AND status='approved'")
        return await cur.fetchall()