from pydantic import BaseModel


class StoreStateRequest(BaseModel):
    agent_id: str
    context_payload: dict


class StoreStateResponse(BaseModel):
    state_id: str


class ScheduleWakeupRequest(BaseModel):
    agent_webhook_url: str
    state_id: str
    execute_at_unix: int


class ScheduleWakeupResponse(BaseModel):
    status: str
    job_id: str
