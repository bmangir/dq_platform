from dq_engine.database.connection import (
    get_postgres_connection_string,
)

import psycopg2


def test_postgres_connection():

    connection_string = (
        get_postgres_connection_string()
    )

    with psycopg2.connect(
            connection_string
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute("SELECT 1")

            result = cursor.fetchone()

    assert result == (1,)