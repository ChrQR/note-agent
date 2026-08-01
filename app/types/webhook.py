from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class WebhookRequestEventEnum(str, Enum):
    transcription_completed = "transcription.completed"
    transcription_edited = "transcription.edited"
    summary_completed = "summary.completed"
    summary_regenerated = "summary.regenerated"
    summary_updated = "summary.updated"
    mind_map_completed = "mind_map.completed"
    action_items_regenerated = "action_items.regenerated"
    action_items_updated = "action_items.updated"
    speakers_labeled = "speakers.labeled"
    recording_created = "recording.created"
    recording_deleted = "recording.deleted"
    recording_merged = "recording.merged"
    translation_completed = "translation.completed"

class WebhookRequestRecordingData(BaseModel):
    id: str
    title: str | None = None
    description: str | None = None
    duration: int | None = None
    language: str | None = None
    created_at: datetime = Field(alias="createdAt")

class WebhookRequest(BaseModel):
    event: WebhookRequestEventEnum
    timestamp: datetime
    recording: WebhookRequestRecordingData
