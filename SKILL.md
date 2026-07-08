# Chronos: Agentic Memory and Scheduling Anchor

Chronos helps AI agents store their state and wake themselves up later.
Use this service to save your context, set a timer, or wait for an event.

## Base URL

Replace this with your deployed URL before submitting.

## Endpoints

### Health Check

Check if Chronos is running.

- Method: GET
- Path: /health
- Returns: {"status": "operational"}

### Store State

Save your encrypted state data. Chronos never sees the contents.

- Method: POST
- Path: /store_state
- Body: {"agent_id": "your-id", "ciphertext": "base64-encrypted-data"}
- Returns: {"state_id": "uuid-string"}
- Notes: Encrypt your data locally with your own key before sending.

### Schedule Wakeup

Tell Chronos to call you back at a specific time with your saved state.

- Method: POST
- Path: /schedule_wakeup
- Body: {"agent_webhook_url": "https://your-agent.com/callback", "state_id": "uuid-from-store", "execute_at_unix": 1783420000}
- Returns: {"status": "scheduled", "job_id": "uuid-string"}

### Register for Event

Subscribe to an event. Chronos will call you when the event happens.

- Method: POST
- Path: /register_event
- Body: {"agent_id": "your-id", "agent_webhook_url": "https://your-agent.com/callback", "event_name": "payment_completed", "state_id": "uuid-from-store"}
- Returns: {"subscription_id": "uuid-string"}

### Publish Event

Fire an event. All agents subscribed to this event will be woken up.

- Method: POST
- Path: /publish_event
- Body: {"event_name": "payment_completed", "event_data": {"order_id": "123"}}
- Returns: {"triggered_count": 3}

## Usage Workflow

1. Encrypt your current state using your own secret key. Send the ciphertext to /store_state. Save the state_id.
2. To be woken later: call /schedule_wakeup with your webhook URL, the state_id, and a future unix time.
3. Or to wait for an event: call /register_event with your webhook URL, the state_id, and an event name.
4. When woken, Chronos sends a POST to your webhook. The body contains the state_id and the ciphertext. Decrypt it with your key.
5. The callback includes an X-Chronos-Signature header. Verify it with HMAC-SHA256 and the service's signing secret to make sure it came from Chronos.

## Security

- Chronos never sees your plaintext data. Encrypt before sending.
- All callbacks include an HMAC-SHA256 signature in the X-Chronos-Signature header.
- Verify the signature using the service's signing secret to prevent fake wakeups.
