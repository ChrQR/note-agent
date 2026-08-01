from contextlib import asynccontextmanager
from app.config import settings
from app.types.vikunja import ListProjectsResponse, CreateTaskRequest, CreateTaskRelationRequest, CreateTaskResponse
from app.services.openrouter import ActionItem
import httpx2 as httpx

class Vikunja:

    def __init__(self, vikunja_api_key):
        self.project_dict: dict[str, int] = {}
        self.client = httpx.AsyncClient(
            base_url="https://todo.rannes.dev/api/v2",
            headers={
                "Authorization": f"Bearer {vikunja_api_key}",
                "Content-Type": "application/json"
            }
        )


    @classmethod
    async def create(cls, vikunja_api_key: str) -> "Vikunja":
        instance = cls(vikunja_api_key)

        projects = await instance.list_projects()
        for project in projects.items:
            instance.project_dict[project.title.lower()] = project.id

        return instance

    async def close(self):
        await self.client.aclose()


    async def create_tasks_from_note(self, meeting_title: str, tasks: list[ActionItem]):
        if len(tasks) <= 1:
            await self.create_task(self.project_dict[tasks[0].project.value if tasks[0].project else "inbox"], tasks[0])
            return

        parent_task_id = await self.create_parent_task(meeting_title, self.project_dict["inbox"])

        for task in tasks:
            await self.create_task(self.project_dict[task.project.value if task.project else "inbox"], task, parent_task_id)

    async def create_task(self, project_id: int, task: ActionItem, parent_id: int | None = None) -> CreateTaskResponse:
        task_resp = await self.client.post(f"/projects/{project_id}/tasks", json=CreateTaskRequest(
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            priority=task.priority.value if task.priority else None
        ).model_dump(mode="json"))

        task_resp.raise_for_status()
        task_data = CreateTaskResponse.model_validate_json(task_resp.content)

        if parent_id:
            await self.create_task_relation(parent_id, task_data.id)

        return task_data



    async def create_parent_task(self, meeting_title: str, project_id: int) -> int:
        resp = await self.create_task(project_id, ActionItem(title=meeting_title))
        return resp.id

    async def create_task_relation(self, parent: int, sub: int):
        resp = await self.client.post(f"/tasks/{parent}/relations", json=CreateTaskRelationRequest(
            other_task_id=sub,
        ).model_dump(mode="json"))
        resp.raise_for_status()

    async def list_projects(self) -> ListProjectsResponse:
        resp = await self.client.get("/projects")
        resp.raise_for_status()

        return ListProjectsResponse.model_validate_json(resp.content)
