from enum import Enum
from datetime import datetime
from pydantic import BaseModel

class ListProjectsResponse(BaseModel):
    items: list[ProjectInfo]
    page: int
    per_page: int
    total: int
    total_pages: int

class ProjectInfo(BaseModel):
    id: int
    title: str
    description: str
    identifier: str
    hex_color: str
    created: datetime

class CreateTaskRequest(BaseModel):
    title: str
    description: str | None
    due_date: datetime | None
    priority: int | None

class CreateTaskResponse(BaseModel):
    id: int


class CreateTaskRelationKind(str, Enum):
    subtask = "subtask"
    parent_task = "parenttask"
    related = "related"
    duplicate_of = "duplicateof"
    duplicates = "duplicates"
    blocking = "blocking"
    blocked = "blocked"
    precedes = "precedes"
    follows = "follows"
    copied_from = "copiedfrom"
    copied_to = "copiedto"

class CreateTaskRelationRequest(BaseModel):
    other_task_id: int
    relation_kind: CreateTaskRelationKind = CreateTaskRelationKind.subtask
