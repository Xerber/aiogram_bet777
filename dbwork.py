from aiomysql import Pool, DictCursor
import pymysql
from connect import db_connect


class DBCommands:
  pool: Pool = db_connect


  async def add_user(self,chat_id,username):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("INSERT INTO users (chat_id,username) VALUES (%s,%s)",(chat_id,username))


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


  async def get_ready(self,match_id):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("SELECT matches.match_id,users.chat_id,users.username FROM `matches_users` LEFT JOIN matches ON matches_users.match_id = matches.id LEFT JOIN users ON matches_users.user_id = users.id WHERE matches.match_id = %s",(match_id))
        return await cur.fetchall()


  async def get_not_ready(self):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("SELECT * from users WHERE role='user' AND status='approved'")
        return await cur.fetchall()


  async def add_user_ready(self,match_id,username):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("INSERT INTO matches_users (match_id,user_id) VALUES ((SELECT id FROM matches WHERE match_id = %s),(SELECT id FROM users WHERE username=%s))",(match_id,username))


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


  async def add_match(self,match_id):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("INSERT INTO matches (match_id) VALUES (%s)",(match_id))


  async def get_match(self,match_id):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("SELECT * from matches WHERE match_id=%s",(match_id))
        return await cur.fetchone()


  async def check_outcome(self,match_id):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("SELECT * FROM matches_users LEFT JOIN matches ON matches_users.match_id = matches.id RIGHT JOIN users ON matches_users.user_id = users.id WHERE matches.match_id = %s",(match_id))
        return await cur.fetchone()


  async def upd_outcome(self,match_id,outcome):
    async with self.pool.acquire() as conn:
      async with conn.cursor(DictCursor) as cur:
        await cur.execute("UPDATE matches SET outcome=%s WHERE match_id=%s",(outcome,match_id))