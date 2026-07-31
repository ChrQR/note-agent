from app.services.openrouter import ActionItem
import httpx2 as httpx

class Vikunja:
    def __init__(self, vikunja_api_key):
        self.client = httpx.AsyncClient(
            base_url="https://todo.rannes.dev/api/v2",
            headers={
                "Authorization": f"Bearer {vikunja_api_key}",
                "Content-Type": "application/json"
            }
        )

    def create_tasks_from_note(self, meeting_title: str, tasks: list[ActionItem]):
        if len(tasks) <= 1:
            self.create_task(tasks[0])
            return

        parent_task_id = self.create_parent_task(meeting_title)

        for task in tasks:
            self.create_task(task, parent_task_id)

    def create_task(self, task: ActionItem, parent_id: int | None = None):
        pass

    def create_parent_task(self, meeting_title: str) -> int:
        pass
