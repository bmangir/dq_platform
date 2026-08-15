import psycopg2
import pytest

from dq_engine.database.connection import (
    get_postgres_connection_string,
)


@pytest.fixture
def postgres_connection():
    connection_string = (
        get_postgres_connection_string()
    )

    connection = psycopg2.connect(
        connection_string
    )

    try:
        yield connection
    finally:
        connection.close()

@pytest.fixture
def reset_orders_table(postgres_connection):

    with postgres_connection.cursor() as cursor:

        cursor.execute(
            """
            TRUNCATE TABLE public.orders;
            """
        )

    postgres_connection.commit()


@pytest.fixture
def valid_orders_data(
        postgres_connection,
        reset_orders_table,
):

    with postgres_connection.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO public.orders
                (
                    order_id,
                    customer_id,
                    order_amount,
                    order_status,
                    order_date
                )
            VALUES
                (1, 101, 120.50, 'completed', '2026-08-01'),
                (2, 102, 250.00, 'completed', '2026-08-02'),
                (3, 103, 89.90, 'pending', '2026-08-03'),
                (NULL, 104, 150.00, 'completed', '2026-08-04'),
                (5, 105, 300.00, 'cancelled', '2026-08-05');
            """
        )

    postgres_connection.commit()


@pytest.fixture
def duplicate_orders_data(
        postgres_connection,
        reset_orders_table,
):

    with postgres_connection.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO public.orders
                (
                    order_id,
                    customer_id,
                    order_amount,
                    order_status,
                    order_date
                )
            VALUES
                (1, 101, 120.50, 'completed', '2026-08-01'),
                (2, 102, 250.00, 'completed', '2026-08-02'),
                (2, 103, 89.90, 'pending', '2026-08-03'),
                (NULL, 104, 150.00, 'completed', '2026-08-04'),
                (5, 105, 300.00, 'cancelled', '2026-08-05');
            """
        )

    postgres_connection.commit()


@pytest.fixture
def invalid_order_status_data(
        postgres_connection,
        reset_orders_table,
):

    with postgres_connection.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO public.orders
                (
                    order_id,
                    customer_id,
                    order_amount,
                    order_status,
                    order_date
                )
            VALUES
                (1, 101, 120.50, 'completed', '2026-08-01'),
                (2, 102, 250.00, 'completed', '2026-08-02'),
                (3, 103, 89.90, 'shipped', '2026-08-03'),
                (4, 104, 150.00, 'completed', '2026-08-04'),
                (5, 105, 300.00, NULL, '2026-08-05');
            """
        )

    postgres_connection.commit()


@pytest.fixture
def null_order_id_data(
        postgres_connection,
        reset_orders_table,
):

    with postgres_connection.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO public.orders
                (
                    order_id,
                    customer_id,
                    order_amount,
                    order_status,
                    order_date
                )
            VALUES
                (1, 101, 120.50, 'completed', '2026-08-01'),
                (2, 102, 250.00, 'completed', '2026-08-02'),
                (3, 103, 89.90, 'pending', '2026-08-03'),
                (NULL, 104, 150.00, 'completed', '2026-08-04'),
                (5, 105, 300.00, 'cancelled', '2026-08-05');
            """
        )

    postgres_connection.commit()


@pytest.fixture
def invalid_order_amount_data(
        postgres_connection,
        reset_orders_table,
):

    with postgres_connection.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO public.orders
                (
                    order_id,
                    customer_id,
                    order_amount,
                    order_status,
                    order_date
                )
            VALUES
                (1, 101, 120.50, 'completed', '2026-08-01'),
                (2, 102, 250.00, 'completed', '2026-08-02'),
                (3, 103, -20.00, 'pending', '2026-08-03'),
                (4, 104, 150.00, 'completed', '2026-08-04'),
                (5, 105, NULL, 'cancelled', '2026-08-05');
            """
        )

    postgres_connection.commit()