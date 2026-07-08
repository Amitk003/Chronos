from fastapi import FastAPI, HTTPException

from app.models import (
    StoreStateRequest,
    StoreStateResponse,
    ScheduleWakeupRequest,
    ScheduleWakeupResponse,
)
from app import storage, scheduler

app = FastAPI(title="Chronos")


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
