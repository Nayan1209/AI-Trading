# AWS Lightsail deployment

This package runs the FastAPI dashboard behind Caddy on an Ubuntu Lightsail instance. Caddy terminates HTTPS and requires HTTP Basic Authentication for the dashboard and account APIs. The app container has no published host port and accepts private account reads only from Caddy's fixed Docker-network address.

This deploys the current read-only Groww integration. It does not enable or submit live orders: the repository has no live order endpoint yet. A confirmation screen, chosen strategy, rupee risk limits, and a Groww-approved unattended credential lifecycle are still required before that work can be enabled.

## AWS resources to create

1. Create an Ubuntu Lightsail instance in a region near you and Groww's API.
2. Attach a Lightsail static IPv4 address. Groww requires a registered static IP for API order placement; register it with Groww before enabling any broker write feature.
3. Allow inbound TCP 80 and 443 for the dashboard. Restrict SSH (TCP 22) to your current public IP.
4. Point a DNS A record for your dashboard hostname to the static IPv4 address. Caddy obtains and renews the HTTPS certificate automatically.
5. Create a PostgreSQL database in the same Lightsail region, enable private access for Lightsail resources, and use a dedicated database/user for this app. Keep the database endpoint and credentials only in the instance's ignored `.env` file.

AWS resources incur charges. Choose instance and database sizes in the Lightsail console based on expected workload and review the monthly estimate before creating them.

## Prepare the instance

Install Docker Engine and the Docker Compose plugin using Docker's official Ubuntu instructions. Clone the GitHub `main` branch onto the instance and enter the repository directory. Copy `.env.example` to `.env`, set its permissions with `chmod 600 .env`, and edit it with `nano .env`.

For production, set `APP_ENV=production`, the database URL, Groww API credentials, dashboard hostname, and TLS email. Set `DASHBOARD_USERNAME` to your login. Generate the password hash using the interactive prompt so the password does not appear in shell history: `docker run --rm -it caddy:2-alpine caddy hash-password`. Put the resulting hash in single quotes on the `DASHBOARD_PASSWORD_HASH` line; the hash contains dollar signs.

Never add `.env` or real Groww credentials to GitHub. The provided `.env.example` contains placeholders only.

## Start and update

From the repository root on the instance, start the app with `docker compose --env-file .env -f deploy/lightsail/compose.yml up -d --build`.

Open `https://<your-dashboard-hostname>/` and sign in with the Basic Auth username and password. Caddy requires authentication for all public routes; the app port is not exposed on the host. The container health check talks to the app directly inside Docker.

To deploy a later `main` update, run `git pull --ff-only origin main` followed by the same `docker compose ... up -d --build` command. Back up the Lightsail database and instance separately.

Monitor the instance and Groww API access. A running VM does not keep a Groww access token or daily approval valid. Confirm the allowed API-key/TOTP renewal process with Groww before relying on unattended operation. Market data and exchange order execution are available only when Groww and the relevant exchange permit them.

## Current blockers for live orders

- The adapter in `src/market_data/groww_provider.py` is explicitly read-only; no live Groww order submission endpoint exists.
- Every order must be presented for your explicit confirmation.
- Your description says to place orders after reading market trends, but the specific strategy and maximum rupee amounts per order and per day are not set.
- Groww quote access previously returned HTTP 403. Confirm the active Trading API subscription and market-data permissions before relying on live quotes.
- Confirm with Groww how cloud API credentials may be refreshed unattended and whether daily approval is required for this account.
- Configure and whitelist the Lightsail static IP with Groww before any broker write feature is implemented.
