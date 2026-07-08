from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.models import (
    StoreStateRequest,
    StoreStateResponse,
    ScheduleWakeupRequest,
    ScheduleWakeupResponse,
    RegisterEventRequest,
    RegisterEventResponse,
    PublishEventRequest,
    PublishEventResponse,
)
from app import storage, scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Chronos", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "operational"}


@app.post("/store_state", response_model=StoreStateResponse)
async def store_state(request: StoreStateRequest):
    state_id = storage.store(request.agent_id, request.ciphertext)
    return StoreStateResponse(state_id=state_id)


@app.post("/schedule_wakeup", response_model=ScheduleWakeupResponse)
async def schedule_wakeup(request: ScheduleWakeupRequest):
    record = storage.get(request.state_id)
    if record is None:
        raise HTTPException(status_code=404, detail="state_id not found")

    job_id = scheduler.schedule_wakeup(
        agent_webhook_url=request.agent_webhook_url,
        state_id=request.state_id,
        execute_at_unix=request.execute_at_unix,
    )
    return ScheduleWakeupResponse(status="scheduled", job_id=job_id)


@app.post("/register_event", response_model=RegisterEventResponse)
async def register_event(request: RegisterEventRequest):
    record = storage.get(request.state_id)
    if record is None:
        raise HTTPException(status_code=404, detail="state_id not found")

    subscription_id = storage.subscribe_event(
        agent_id=request.agent_id,
        agent_webhook_url=request.agent_webhook_url,
        event_name=request.event_name,
        state_id=request.state_id,
    )
    return RegisterEventResponse(subscription_id=subscription_id)


@app.post("/publish_event", response_model=PublishEventResponse)
async def publish_event(request: PublishEventRequest):
    triggered = scheduler.trigger_event(
        event_name=request.event_name,
        event_data=request.event_data,
    )
    return PublishEventResponse(triggered_count=triggered)
