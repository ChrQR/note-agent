import json
from pydantic import ValidationError

import httpx2 as httpx

from app.types.pocket_api import GetRecordingResponse, ListRecordingsResponse


class PocketService:
    def __init__(self, pocket_api_key):
        self.pocket_api_key = pocket_api_key
        self.base_url = "https://public.heypocketai.com/api/v1/public"
        self.client = httpx.Client(
            headers={"Authorization": f"Bearer {self.pocket_api_key}"},
            base_url=self.base_url
        )

    def list_recordings(self) -> ListRecordingsResponse | None:
        with self.client as client:
            try:
                resp = client.get(
                    "/recordings",
                )

                return ListRecordingsResponse.model_validate_json(resp.content)
            except ValidationError as e:
                print(f"Error validating response: {e}")

    def get_recording_by_id(self, id: str) -> GetRecordingResponse | None:
        with self.client as client:
            try:
                resp = client.get(f"/recordings/{id}")

                return GetRecordingResponse.model_validate_json(resp.content)
            except ValidationError as e:
                print(f"Error validating response: {e}")
