from contextlib import asynccontextmanager
from app.types.webhook import WebhookRequest, WebhookRequestEventEnum
from fastapi import FastAPI, Response, Request
import logfire
from app.services.vikunja import Vikunja
from app.services.openrouter import NoteParser

from app.config import settings
from app.services.pocket import PocketService


@asynccontextmanager
async def lifespan(app: FastAPI):
    vikunja = await Vikunja.create(settings.vikunja_api_key)
    pocket_service = PocketService(settings.pocket_api_key)
    agent = NoteParser(settings.openrouter_api_key, settings.model_name)
    yield {
        "vikunja": vikunja,
        "agent": agent,
        "pocket_service": pocket_service
    }

    await vikunja.close()

app = FastAPI(lifespan=lifespan)

logfire.configure()
logfire.instrument_system_metrics()
logfire.instrument_pydantic_ai()
logfire.instrument_httpx()
logfire.instrument_fastapi(app=app)

@app.post("/webhook")
async def webhook(request: Request, data: WebhookRequest):
    if data.event is not WebhookRequestEventEnum.summary_completed:
        return Response(status_code=200)

    agent: NoteParser = request.state.agent
    pocket_client: PocketService = request.state.pocket_service
    vikunja_client: Vikunja = request.state.vikunja


    recording = await pocket_client.get_recording_by_id(data.recording.id)
    if recording is not None and recording.data is not None:
        result = await agent.parse_pocket_recording(recording, True)
        if result is not None:
            if result.todo is not None:
                await vikunja_client.create_tasks_from_note(recording.data.title, result.todo)

    return {"parsing": "success"}
