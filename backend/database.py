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

            search = f"%{query}%"

            cur.execute("""
                SELECT
                    title,
                    url,
                    content,

                    (
                        CASE
                            WHEN title ILIKE %s
                            THEN 100
                            ELSE 0
                        END
                    )

                    +

                    (
                        CASE
                            WHEN url ILIKE %s
                            THEN 50
                            ELSE 0
                        END
                    )

                    +

                    (
                        LENGTH(content)
                        -
                        LENGTH(
                            REPLACE(
                                LOWER(content),
                                LOWER(%s),
                                ''
                            )
                        )
                    )

                    AS score

                FROM documents

                WHERE
                    title ILIKE %s
                    OR url ILIKE %s
                    OR content ILIKE %s

                ORDER BY score DESC

                LIMIT 50

            """, (
                search,
                search,
                query,
                search,
                search,
                search
            ))

            return cur.fetchall()

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
