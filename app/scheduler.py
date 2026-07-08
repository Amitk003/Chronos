import uuid
import logging
from datetime import datetime, timezone

import httpx
from apscheduler.schedulers.background import BackgroundScheduler

from app import storage

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler()
_scheduler.start()


def schedule_wakeup(
    agent_webhook_url: str,
    state_id: str,
    execute_at_unix: int,
) -> str:
    job_id = str(uuid.uuid4())
    run_date = datetime.fromtimestamp(execute_at_unix, tz=timezone.utc)

    _scheduler.add_job(
        func=_send_webhook,
        trigger="date",
        run_date=run_date,
        args=[agent_webhook_url, state_id],
        id=job_id,
    )

    logger.info("Scheduled wakeup job %s at %s", job_id, run_date)
    return job_id


def _send_webhook(agent_webhook_url: str, state_id: str) -> None:
    record = storage.get(state_id)
    if record is None:
        logger.warning("State %s not found for webhook", state_id)
        return

    payload = {
        "state_id": state_id,
        "context_payload": record["context_payload"],
    }

    try:
        response = httpx.post(agent_webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Webhook sent to %s for state %s", agent_webhook_url, state_id)
    except httpx.HTTPError as e:
        logger.error("Webhook failed for %s: %s", agent_webhook_url, e)
