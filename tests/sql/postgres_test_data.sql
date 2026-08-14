CREATE TABLE IF NOT EXISTS public.orders (
    order_id INTEGER,
    customer_id INTEGER,
    order_amount NUMERIC(12, 2),
    order_status VARCHAR(50),
    order_date TIMESTAMP
);

TRUNCATE TABLE public.orders;

INSERT INTO public.orders
    (order_id, customer_id, order_amount, order_status, order_date)
VALUES
    (1, 101, 120.50, 'completed', '2026-08-01'),
    (2, 102, 250.00, 'completed', '2026-08-02'),
    (3, 103, 89.90, 'pending', '2026-08-03'),
    (NULL, 104, 150.00, 'completed', '2026-08-04'),
    (5, 105, 300.00, 'cancelled', '2026-08-05');