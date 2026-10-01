CREATE TABLE IF NOT EXISTS candles (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    exchange TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open NUMERIC(28, 10) NOT NULL,
    high NUMERIC(28, 10) NOT NULL,
    low NUMERIC(28, 10) NOT NULL,
    close NUMERIC(28, 10) NOT NULL,
    volume BIGINT NOT NULL CHECK (volume >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (symbol, exchange, timeframe, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_candles_lookup
    ON candles (exchange, symbol, timeframe, timestamp);
