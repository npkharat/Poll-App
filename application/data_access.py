"""
TIER 2: APPLICATION LAYER — DATA ACCESS
============================================================
Only this file talks to the database. No percentage math,
no validation - that's logic.py's job.
============================================================
"""
import pymysql
from pymysql.cursors import DictCursor
from config import Config


def get_connection():
    return pymysql.connect(
        host=Config.DB_HOST, port=Config.DB_PORT, user=Config.DB_USER,
        password=Config.DB_PASSWORD, database=Config.DB_NAME,
        cursorclass=DictCursor, autocommit=True,
    )


def create_poll(question, options):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO polls (question) VALUES (%s)", (question,))
            poll_id = cur.lastrowid
            for opt in options:
                cur.execute(
                    "INSERT INTO poll_options (poll_id, option_text) VALUES (%s, %s)",
                    (poll_id, opt.strip()),
                )
            return poll_id
    finally:
        conn.close()


def list_polls():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM polls ORDER BY created_at DESC")
            polls = cur.fetchall()
            for poll in polls:
                cur.execute(
                    "SELECT id, option_text, votes FROM poll_options WHERE poll_id = %s ORDER BY id",
                    (poll["id"],),
                )
                poll["_options"] = cur.fetchall()
            return polls
    finally:
        conn.close()


def get_poll(poll_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM polls WHERE id = %s", (poll_id,))
            poll = cur.fetchone()
            if not poll:
                return None
            cur.execute(
                "SELECT id, option_text, votes FROM poll_options WHERE poll_id = %s ORDER BY id",
                (poll_id,),
            )
            poll["_options"] = cur.fetchall()
            return poll
    finally:
        conn.close()


def cast_vote(poll_id, option_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE poll_options SET votes = votes + 1 WHERE id = %s AND poll_id = %s",
                (option_id, poll_id),
            )
            return cur.rowcount
    finally:
        conn.close()


def delete_poll(poll_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM polls WHERE id = %s", (poll_id,))
            return cur.rowcount
    finally:
        conn.close()
