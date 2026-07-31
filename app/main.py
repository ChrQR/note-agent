from app.services.openrouter import NoteParser
import asyncio

from app.config import settings
from app.services.pocket import PocketService

from rich import print


async def main():
    pocket_service = PocketService(settings.pocket_api_key)
    agent = NoteParser(settings.openrouter_api_key, settings.model_name)

    data = pocket_service.get_recording_by_id("17a95d01-e470-412a-a2b8-06bb67cf83e5")
    if data is not None:
        print(await agent.parse_pocket_recording(data, True))


if __name__ == "__main__":
    asyncio.run(main())
