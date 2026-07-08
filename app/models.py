from typing import Any, Optional

from pydantic import BaseModel


class StoreStateRequest(BaseModel):
    agent_id: str
    ciphertext: str


class StoreStateResponse(BaseModel):
    state_id: str


class ScheduleWakeupRequest(BaseModel):
    agent_webhook_url: str
    state_id: str
    execute_at_unix: int


class ScheduleWakeupResponse(BaseModel):
    status: str
    job_id: str


class RegisterEventRequest(BaseModel):
    agent_id: str
    agent_webhook_url: str
    event_name: str
    state_id: str


class RegisterEventResponse(BaseModel):
    subscription_id: str


class PublishEventRequest(BaseModel):
    event_name: str
    event_data: Optional[dict[str, Any]] = None


class PublishEventResponse(BaseModel):
    triggered_count: int
