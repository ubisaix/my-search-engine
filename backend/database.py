import os
import psycopg


DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    return psycopg.connect(DATABASE_URL)


def create_table():

    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    content TEXT NOT NULL
                )
            """)

        conn.commit()


def add_document(title, url, content):

    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO documents
                (title, url, content)
                VALUES (%s, %s, %s)
                ON CONFLICT (url)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    content = EXCLUDED.content
            """, (title, url, content))

        conn.commit()


def search_documents(query):

    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute("""
                SELECT title, url, content
                FROM documents
                WHERE
                    title ILIKE %s
                    OR content ILIKE %s
                LIMIT 50
            """, (
                f"%{query}%",
                f"%{query}%"
            ))

            return cur.fetchall()
