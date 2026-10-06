# UI/UX Specification
**Version:** 0.2 | **Status:** Initial read-only development command center implemented; operational screens remain draft

## Screens
Login/MFA; Command Center; Scanner; Signals; AI Analysis; Trade Plans; Orders; Positions; Portfolio; Trade Journal; Risk Center; System Health; Audit Log; Settings; Emergency Controls.

## Command Center
Show system state, portfolio, P&L, drawdown, exposure, positions, AI decisions, orders, risk state, and data/broker health.

### Initial UI-001 Delivery

The first dashboard slice is served at `/` by the FastAPI application and consumes the health and latest-market-data endpoints plus optional read-only paper and Groww account snapshots.

- Shows whether the application health endpoint responds and the reported environment.
- Lets the user request a live quote or latest 15-minute candle by symbol and exchange.
- Identifies Groww as the quote source and states that live execution is disabled.
- Shows current-process paper orders and positions and, when configured, the PostgreSQL paper-order journal and Groww holdings, positions, and current-day orders.
- Shows explicit unconfigured/unavailable states when credentials, `DATABASE_URL`, or migration 003 are unavailable. It must not invent prices, balances, P&L, decisions, orders, or risk state.
- Provides no order entry, cancellation, trading-halt, credential, or other write controls.
- Keeps unauthenticated paper and account snapshot APIs on development mode and loopback clients only.
- Uses native HTML/CSS/JavaScript with no external script, font, image, or chart dependency.

This initial view is development-only. It does not implement login/MFA. Do not expose it as a production dashboard until authentication and authorization are in place.

Signals, AI decisions, risk, and live-execution health remain disconnected. The PostgreSQL journal stores paper fills only; the dashboard reconstructs paper positions and realized P&L from those fills and does not estimate unrealized P&L without price marks.

## Principles
Trading state must be unambiguous. Risk is prominent. Dangerous actions require confirmation. Emergency stop is easy to locate. AI analysis uses structured reason codes/evidence. Color is never the only indicator.
