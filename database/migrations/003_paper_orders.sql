CREATE TABLE IF NOT EXISTS paper_orders (
    order_id TEXT PRIMARY KEY,
    client_order_id TEXT NOT NULL UNIQUE,
    internal_id TEXT NOT NULL,
    trading_symbol TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('BUY', 'SELL')),
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    fill_price NUMERIC(28, 10) NOT NULL CHECK (fill_price > 0),
    status TEXT NOT NULL CHECK (status = 'FILLED'),
    created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_paper_orders_history
    ON paper_orders (created_at, order_id);
