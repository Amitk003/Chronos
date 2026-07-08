import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from app import storage
from app.crypto import sign_payload
from app.config import settings

logger = logging.getLogger(__name__)

_scheduler: Optional[BackgroundScheduler] = None


def start(jobs_db_url: Optional[str] = None) -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)

    url = jobs_db_url if jobs_db_url is not None else settings.jobs_db_url
    engine_options = {"connect_args": {"check_same_thread": False}}
    jobstores = {
        "default": SQLAlchemyJobStore(url=url, engine_options=engine_options),
    }
    _scheduler = BackgroundScheduler(jobstores=jobstores)
    _scheduler.start()
    logger.info("Scheduler started with job store: %s", url)


def shutdown() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler shut down")


def schedule_wakeup(
    agent_webhook_url: str,
    state_id: str,
    execute_at_unix: int,
) -> str:
    if _scheduler is None:
        raise RuntimeError(
            "Scheduler not started. Call scheduler.start() first."
        )

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


def trigger_event(event_name: str, event_data: Optional[dict] = None) -> int:
    subscriptions = storage.get_subscriptions_by_event(event_name)
    if not subscriptions:
        logger.info("No subscriptions for event: %s", event_name)
        return 0

    triggered = 0
    for sub in subscriptions:
        state_id = sub["state_id"]
        record = storage.get(state_id)
        if record is None:
            logger.warning("State %s not found for event %s", state_id, event_name)
            continue

        payload = {
            "event": event_name,
            "state_id": state_id,
            "ciphertext": record["ciphertext"],
        }
        if event_data is not None:
            payload["event_data"] = event_data

        signature = sign_payload(payload, settings.signing_secret)
        headers = {
            "Content-Type": "application/json",
            "X-Chronos-Signature": signature,
        }

        transport = httpx.HTTPTransport(retries=3)
        try:
            with httpx.Client(transport=transport, timeout=15) as client:
                response = client.post(
                    sub["agent_webhook_url"], json=payload, headers=headers
                )
                response.raise_for_status()
                logger.info(
                    "Event webhook sent to %s for event %s",
                    sub["agent_webhook_url"],
                    event_name,
                )
                storage.delete(state_id)
                triggered += 1
        except httpx.HTTPError as e:
            logger.error(
                "Event webhook failed for %s: %s",
                sub["agent_webhook_url"],
                e,
            )

    return triggered


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
