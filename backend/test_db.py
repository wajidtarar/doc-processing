import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ["DATABASE_URL"]

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        print("Connected! Postgres version:")
        print(cur.fetchone()[0])