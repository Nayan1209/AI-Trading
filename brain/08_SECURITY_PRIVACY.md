# Security & Privacy Specification
**Version:** 0.2 | **Status:** Active Draft

## Objectives
Confidentiality, integrity, availability, least privilege, traceability, and safe failure.

## Secrets
Never store credentials in source or documentation. Inject secrets at runtime using environment/secret management. Never log API keys, API secrets, access tokens, TOTP values, broker passwords or trading PINs.

The project owner has confirmed that a Groww API key exists and is approved. The key material itself is intentionally not recorded in this repository.

## Groww Credential Lifecycle
Groww documents access-token authentication and API-key/secret and TOTP-based flows. The integration must treat access tokens as short-lived runtime credentials. The current Groww documentation states that access tokens expire daily at 6:00 AM and that API-key/secret and TOTP token generation may require daily approval on the Groww Cloud API Keys page.

The application must:
- generate or obtain tokens only at runtime;
- keep secrets outside Git;
- redact credentials from logs/errors;
- rotate/revoke compromised credentials;
- fail closed when authentication is unavailable.

## Access
Roles: Owner/Admin, Operator, Read-only/Analyst, Service Account. Trading execution permissions are separate from administration.

## AI Security
Treat news/web text as untrusted. Defend against prompt injection. Tool access is allow-listed. AI has no withdrawal/bank-change capability and does not receive raw broker credentials.

## Network
TLS, firewall/allow-listing, applicable static-IP requirements, private database networking, and no public database exposure.

For production Groww order placement, use a controlled runtime with a registered static public IP. Do not whitelist arbitrary dynamic personal-network addresses as the production trading endpoint.

## Execution Safety
- Development and paper environments cannot place live orders.
- Every live order must pass deterministic risk checks.
- AI output cannot bypass risk, position, exposure, loss or trading-halt controls.
- Kill switch/trading halt must be available independently of the AI model.
- Reconciliation mismatches must block further execution until resolved.

## Audit
Authentication events, configuration changes, AI decisions, risk decisions, order actions, broker responses, static-IP configuration changes, and system-control events must be auditable.

Audit records must not contain raw secrets.

## Privacy
Minimize personal data and define retention/deletion rules before production.
