---
title: Chronos
emoji: 🕐
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Chronos

Temporal state persistence and wakeup scheduling for stateless AI agents.

```bash
pip install -e . && uvicorn app.main:app --port 8000
```

## Features

- **Store state** — Persist encrypted agent context to SQLite
- **Schedule wakeup** — Request a webhook callback at a future Unix timestamp
- **Event triggers** — Subscribe to named events; Chronos publishes to all subscribers
- **Zero-knowledge** — Agents encrypt payloads locally with Fernet; Chronos stores opaque ciphertext
- **Signed callbacks** — All outbound webhooks carry an HMAC-SHA256 `X-Chronos-Signature` header
- **Cold-start tolerant** — Retries with exponential backoff on serverless 503s

## API

| Method | Path | Request | Response |
|--------|------|---------|----------|
| `GET` | `/health` | — | `{"status": "operational"}` |
| `POST` | `/store_state` | `{agent_id, ciphertext}` | `{state_id}` |
| `POST` | `/schedule_wakeup` | `{agent_webhook_url, state_id, execute_at_unix}` | `{status, job_id}` |
| `POST` | `/register_event` | `{agent_id, agent_webhook_url, event_name, state_id}` | `{subscription_id}` |
| `POST` | `/publish_event` | `{event_name, event_data?}` | `{triggered_count}` |

## Stack

| Layer | Choice |
|-------|--------|
| Framework | FastAPI |
| Scheduler | APScheduler + SQLAlchemy |
| Storage | SQLite |
| Encryption | Fernet (symmetric, AES-128-CBC) |
| Signing | HMAC-SHA256 |
| Runtime | Python 3.11 / Docker |

## Testing

```bash
pytest -v
```
