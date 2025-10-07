# Table ownership and references

This file was generated automatically to map DB tables to files that reference or create them.

## Application-facing tables

- users
  - `services/models/user.py` (ORM model)
  - `services/api/auth.py` (register/login/update/change-tier)
  - `services/api/payments_api.py` (FK references)

- payments
  - `services/api/payments_api.py` (Payment model, endpoints)
  - `services/tmp_test_payments.py` (test client)

- checkout_sessions
  - `services/api/payments_api.py` (CheckoutSession model and endpoints)

- usage_metrics
  - `services/models/usage.py` (ORM model)
  - `services/middleware/event_logger.py` (writes/increments usage)
  - `services/api/auth.py` (calls increment_usage_metrics on register/login)

- weather_data
  - `services/data/PstDB.sql` (CREATE TABLE)
  - `services/agents/collector.py` (to_sql, INSERT into weather_data)
  - `services/agents/TrendAgent.py` (SELECT * FROM weather_data)
  - `services/agents/report.py` (SELECT * FROM weather_data)
  - `services/api/weather_api.py` (former router — used SELECT queries; may have been removed)

- air_quality_data
  - `services/data/PstDB.sql` (CREATE TABLE)
  - `services/agents/collector.py` (INSERT INTO air_quality_data)

## Agent / Audit / Security tables

- security_alerts
  - `services/agents/security_agent.py` (CREATE/INSERT/SELECT)
  - `services/agents/security_framework.py` (scheduling, references)
  - `services/agents/enhanced_orchestrator.py` (references)

- security_audit_log
  - `services/agents/security_agent.py` (CREATE/INSERT)

- data_validation_log
  - `services/agents/security_agent.py` (CREATE/INSERT)

- security_incidents
  - `services/agents/security_framework.py` (CREATE/INSERT/DELETE)
  - `services/api/security_api.py` (GET security incidents)

- system_metrics
  - `services/agents/security_framework.py` (CREATE/INSERT/DELETE)

- api_access_log
  - `services/agents/security_framework.py` (CREATE/SELECT)
  - `services/middleware/event_logger.py` (INSERT)

- network_traffic
  - `services/agents/security_framework.py` (CREATE)

- auth_events
  - `services/agents/security_framework.py` (CREATE/INSERT)
  - `services/middleware/event_logger.py` (INSERT)
  - `services/api/auth.py` (calls log_auth_event)

## Responsible-AI / Ethics tables

- ethics_reports
  - `services/agents/responsible_ai.py` (CREATE/INSERT)

- bias_detection_log
  - `services/agents/responsible_ai.py` (CREATE/INSERT)

- fairness_metrics_log
  - `services/agents/responsible_ai.py` (CREATE/INSERT)

- ai_decision_audit
  - `services/agents/responsible_ai.py` (CREATE/INSERT)

## Notes and instrumentation status

- The middleware `services/middleware/event_logger.py` and the global request middleware in `services/main.py` will create `api_access_log` rows for each request.
- `auth` endpoints now call `log_auth_event` and `increment_usage_metrics` (register, login, logout).
- Payments endpoints already write to `payments` and `checkout_sessions`; I can add audit calls to `auth_events`/`api_access_log` if you want.
- Agent modules under `services/agents/` create their own monitoring/audit tables and already insert rows; they are left as-is.

If you want, I can now:
- Instrument the public API modules (payments, billing, marketplace, orchestrator, analytics, security_api, ai_ethics_api) to add audit calls (recommended).
- Produce a `scripts/dump_recent_events.py` that prints recent rows from `api_access_log`, `auth_events`, and `usage_metrics` for quick verification.
