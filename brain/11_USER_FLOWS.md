# User Flows
**Version:** 0.1 | **Status:** Draft

## Autonomous Trade
Market Event → Candidate → Signal → AI Decision → Trade Plan → Risk Check → Execution → Broker Confirmation → Monitoring → Exit → Journal.

## Rejected Trade
Candidate → AI → Plan → Risk FAIL → No Order → Audit.

## Broker Failure
Execution → Error/Timeout → Retry policy → Reconciliation → Safe State → Alert.

## Market Data Failure
Data issue → Stop new trading → Restore feed → Validate → Resume only when safe.

## Emergency Halt
Kill switch → Block new orders → Handle eligible pending orders → Monitor positions → Safe Mode → Audit.