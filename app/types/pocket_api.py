from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GetRecordingResponse(BaseModel):
    success: bool
    data: RecordingData | None
    pagination: PaginationInfo | None = None
    error: str | None = None


class PaginationInfo(BaseModel):
    has_more: bool
    limit: int
    page: int
    total: int
    total_pages: int


class RecordingMetaData(BaseModel):
    duration: float
    language: str | None = None
    language_probability: float | None = None
    source: str


class RecordingSegment(BaseModel):
    start: float
    end: float
    originalText: str
    text: str


class RawRecordingSegment(BaseModel):
    start: float
    end: float
    text: str


class RecordingTranscriptData(BaseModel):
    metadata: RecordingMetaData
    segments: list[RecordingSegment]
    text: str


class RawRecordingTranscriptData(BaseModel):
    metadata: RecordingMetaData
    segments: list[RawRecordingSegment]
    text: str

class Tag(BaseModel):
    id: str
    name: str
    color: str | None

class RecordingData(BaseModel):
    id: str
    title: str
    duration: int = Field(description="duration in seconds rounded down")
    state: str
    language: str | None = None
    recording_at: datetime
    created_at: datetime
    updated_at: datetime
    tags: list[Tag] | None
    transcript: RecordingTranscriptData
    raw_transcript: RawRecordingTranscriptData
    summarizations: dict[str, Summarization]


class Summarization(BaseModel):
    id: str
    summarizationId: str
    processingStatus: str
    v2: V2


class V2(BaseModel):
    summary: Summary
    mindMap: MindMap
    actionItems: ActionsItems


class ActionsItems(BaseModel):
    actions: list[ActionItem]
    message: str | None
    notification_message: str | None
    version: str


class ActionItem(BaseModel):
    assignee: str
    context: str
    dueDate: datetime | None
    globalActionItemId: str
    id: str
    isCompleted: bool
    is_completed: bool
    label: str
    payload: dict[str, dict[str, Any]]
    priority: str
    status: str
    type: str


class Summary(BaseModel):
    markdown: str
    version: str


class MindMap(BaseModel):
    nodes: list[MindmapNode]
    type: str


class MindmapNode(BaseModel):
    color: str
    node_id: str
    parent_node_id: str
    title: str


class ListRecordingsResponse(BaseModel):
    success: bool
    data: list[RecordingInfo]
    pagination: PaginationInfo | None = None
    error: str | None = None

class RecordingInfo(BaseModel):
    id: str
    title: str
    duration: int | None
    state: str
    language: str | None = None
    recording_at: datetime
    created_at: datetime
    updated_at: datetime
    tags: list[Tag]
