CREATE TABLE IF NOT EXISTS ltp_events (
    id BIGSERIAL PRIMARY KEY,
    internal_id TEXT NOT NULL,
    trading_symbol TEXT NOT NULL,
    exchange TEXT NOT NULL,
    segment TEXT NOT NULL,
    exchange_token TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    ltp NUMERIC(28, 10) NOT NULL CHECK (ltp > 0),
    received_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (internal_id, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_ltp_events_lookup
    ON ltp_events (exchange, segment, exchange_token, timestamp);
