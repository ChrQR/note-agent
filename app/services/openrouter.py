from pydantic_ai.tools import AgentDepsT
from typing import cast
from app.types.pocket_api import RecordingData, GetRecordingResponse
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openrouter import OpenRouterModelSettings, OpenRouterModel


class NoteParser():
    def __init__(self, openrouter_api_key: str, model_name: str):
        settings = OpenRouterModelSettings(
            openrouter_cache_instructions=True,
        )

        model = OpenRouterModel(
            settings=settings,
            model_name=model_name,
        )

        instructions = """
                You are an expert AI assistant that processes meeting transcripts and extracts structured action items and tags.

                Context about the projects and domains:
                * Quantified Impacts (QI): A legacy SaaS platform currently in maintenance mode. Action items here typically involve bug fixes, support, or migrating users and features over to Releaf.
                * Releaf: The primary new SaaS product in active development. Tasks often involve backend and infrastructure development (e.g., Go, Python, Kubernetes, Scaleway Kapsule migration) and collaborating with the product manager, Kristian.
                * Winebucket: A separate project. Tag any tasks specifically mentioning 'Winebucket' or related contexts here.
                * Personal: Home life, personal errands, or administrative tasks unrelated to software development.

                Your task is to review the transcript and:
                1. Assign one or more overall tags to the meeting from the TagEnum.
                2. Extract all action items and categorize them strictly using the project field on the todo item.
                3. For each action item, provide a clear, actionable title, and a detailed description that captures the full context of the task.
                4. Estimate the priority based on urgency language in the text, and format any deadlines as standard timestamps.
                """

        self.agent = Agent(
            model=model,
            output_type=NoteParserOutput,
            instructions=instructions
        )

        @self.agent.system_prompt
        def add_current_datetime(ctx: RunContext[AgentDepsT]) -> str:
            now = datetime.now()
            return f"The current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}. Use this to resolve relative times like 'today', 'tomorrow', or 'next week'."


    async def parse_pocket_recording(
        self,
        response: GetRecordingResponse,
        include_raw_transcript: bool = False
    ) -> NoteParserOutput | None:
        if not response.success or not response.data:
            print(f"Recording payload error: {response.error or 'No recording data'}")
            return None

        formatted_input = format_pocket_recording(
            recording=response.data,
            include_raw_transcript=include_raw_transcript
        )

        result = await self.agent.run(formatted_input)
        return cast(NoteParserOutput, result.output)


class TagEnum(str, Enum):
    releaf = "releaf"
    quantified_impacts = "quantified impacts"
    winebucket = "winebucket"
    personal = "personal"

class ActionItemTagEnum(str, Enum):
    releaf = "releaf"
    quantified_impacts = "quantified_impacts"
    winebucket = "winebucket"
    personal = "personal"

class ActionItem(BaseModel):
    project: ActionItemTagEnum | None = None
    title: str
    description: str | None = None
    priority: ActionItemPriorityEnum | None = Field(default=None, description="This represents the priority of the task where 1 is the lowest priority and 4 is the highest most urgent priority.")
    assigned_to: str | None = None
    due_date: datetime | None = Field(
            default=None,
            description=(
                "The specific date and time this task is due or occurring. "
                "IMPORTANT: If the text mentions relative times like 'i morgen' (tomorrow), "
                "calculate the exact datetime using the current date provided in the system prompt."
            ))

class ActionItemPriorityEnum(Enum):
    low = 1
    medium = 2
    high = 3
    urgent = 4

class NoteParserOutput(BaseModel):
    tags: list[TagEnum]
    todo: list[ActionItem] | None


def format_pocket_recording(
    recording: RecordingData,
    include_raw_transcript: bool = False
) -> str:
    """Formats Pocket recording data into a structured context block for the LLM."""

    parts = []

    date_str = recording.recording_at.strftime("%Y-%m-%d %H:%M")
    parts.append(f"Meeting Title: {recording.title}")
    parts.append(f"Recorded At: {date_str}")
    parts.append(f"Duration: {recording.duration // 60} minutes\n")

    summaries = []
    if recording.summarizations:
        for _, sum_data in recording.summarizations.items():
            if sum_data.v2 and sum_data.v2.summary and sum_data.v2.summary.markdown:
                summaries.append(sum_data.v2.summary.markdown)

    if summaries:
        parts.append("=== POCKET SUMMARY ===")
        parts.append("\n\n".join(summaries))
        parts.append("=====================\n")

    if include_raw_transcript or not summaries:
        parts.append("=== FULL TRANSCRIPT ===")
        if recording.transcript and recording.transcript.text:
            parts.append(recording.transcript.text)
        elif recording.raw_transcript and recording.raw_transcript.text:
            parts.append(recording.raw_transcript.text)
        parts.append("=======================")

    return "\n".join(parts)
