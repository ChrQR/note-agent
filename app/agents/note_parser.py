from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel, OpenRouterModelSettings
from pydantic_ai.providers.openrouter import OpenRouterProvider


class NoteParserAgent:
    def __init__(self, openrouter_api_key: str):
        model_settings = OpenRouterModelSettings(
            openrouter_cache_instructions=True,
        )
        model = OpenRouterModel(
            model_name="deepseek/deepseek-v4-flash",
            provider=OpenRouterProvider(api_key=openrouter_api_key),
        )

        self.agent = Agent(model=model, model_settings=model_settings)

    def run(self, transcript: str):
        self.agent.run_sync(transcript)
