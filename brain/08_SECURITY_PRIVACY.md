# Security & Privacy Specification
**Version:** 0.1 | **Status:** Draft

## Objectives
Confidentiality, integrity, availability, least privilege, traceability, and safe failure.

## Secrets
Never store credentials in source. Inject at runtime using environment/secret management. Never log tokens.

## Access
Roles: Owner/Admin, Operator, Read-only/Analyst, Service Account. Trading execution permissions are separate from administration.

## AI Security
Treat news/web text as untrusted. Defend against prompt injection. Tool access is allow-listed. AI has no withdrawal/bank-change capability.

## Network
TLS, firewall/allow-listing, applicable static-IP requirements, and no public database exposure.

## Audit
Authentication events, configuration changes, AI decisions, risk decisions, order actions, broker responses, and system-control events must be auditable.

## Privacy
Minimize personal data and define retention/deletion rules before production.
