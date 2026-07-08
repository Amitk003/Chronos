import uuid
import logging
from datetime import datetime, timezone

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from app import storage
from app.crypto import sign_payload
from app.config import settings

logger = logging.getLogger(__name__)

jobstores = {
    "default": SQLAlchemyJobStore(url="sqlite:///chronos_jobs.sqlite"),
}
_scheduler = BackgroundScheduler(jobstores=jobstores)
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
        "ciphertext": record["ciphertext"],
    }

    signature = sign_payload(payload, settings.signing_secret)
    headers = {
        "Content-Type": "application/json",
        "X-Chronos-Signature": signature,
    }

    transport = httpx.HTTPTransport(retries=3)
    try:
        with httpx.Client(transport=transport, timeout=15) as client:
            response = client.post(
                agent_webhook_url, json=payload, headers=headers
            )
            response.raise_for_status()
            logger.info(
                "Webhook sent to %s for state %s",
                agent_webhook_url,
                state_id,
            )
            storage.delete(state_id)
    except httpx.HTTPError as e:
        logger.error(
            "Webhook failed for %s after retries: %s",
            agent_webhook_url,
            e,
        )
