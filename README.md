# Chronos

Chronos is a web service that helps AI agents store their state and
wake themselves up later. It acts like an external memory and alarm
clock for agents that would otherwise forget everything when they
shut down.

## What it does

- **Store state** - An agent can save its current context (thoughts,
  conversation history, task progress) to the service.
- **Schedule wakeup** - An agent can ask Chronos to call it back at a
  specific time, with its saved state.
- **Zero-knowledge storage** - Agents encrypt their data before sending
  it. Chronos never sees the actual content.
- **Signed wakeups** - All callback requests are signed so the agent
  can verify they came from Chronos.
- **Retry on failure** - If the agent's server is waking up from sleep,
  Chronos will retry a few times before giving up.
- **Event triggers** - Agents can also wake up when an external event
  happens, not just at a set time.

## Quick start

```bash
# Install dependencies
pip install -e .

# Run the server
uvicorn app.main:app --reload --port 8000
```

## Endpoints

| Method | Path | What it does |
|--------|------|-------------|
| GET | /health | Check if the service is running |
| POST | /store_state | Save agent state (encrypted ciphertext) |
| POST | /schedule_wakeup | Schedule a callback to the agent |
| POST | /register_event | Subscribe to an event trigger |
| POST | /publish_event | Fire an event, wake all subscribers |

## Deploy to Hugging Face Spaces

1. Fork or push this repo to your GitHub account.
2. Go to https://huggingface.co/new-space
3. Name your space (e.g. "chronos-service").
4. Select "Docker" as the Space SDK.
5. Paste your GitHub repo URL.
6. The Dockerfile in this repo will build and start the service.
7. Once deployed, your service will be at
   https://your-username-chronos-service.hf.space

The service listens on port 7860 by default (Hugging Face Spaces
standard). Set the PORT environment variable in the Space settings if
you need a different port.

## Testing

```bash
pytest -v
```
