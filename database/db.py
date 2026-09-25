import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=os.getenv("DATABASE_URL") + "?sslmode=require",
        )
    return _pool


def get_conn():
    return get_pool().getconn()


def release_conn(conn):
    get_pool().putconn(conn)
 

def check_roster(student_id):
    student_id = student_id.strip().upper()
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM official_roster WHERE student_id = %s",
                (student_id,)
            )
            result = cur.fetchone()
        return result is not None
    finally:
        release_conn(conn) 

def is_already_registered(telegram_user_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM registrations WHERE telegram_user_id = %s",
                (telegram_user_id,)
            )
            result = cur.fetchone()
        return result is not None
    finally:
        release_conn(conn)


def insert_registration(name, student_id, telegram_user_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO registrations (name, student_id, telegram_user_id) VALUES (%s, %s, %s)",
                (name, student_id, telegram_user_id)
            )
        conn.commit()
    finally:
        release_conn(conn)