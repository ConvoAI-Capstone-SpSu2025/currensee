from enum import StrEnum, auto
from typing import TypeAlias, Optional
from pydantic import BaseModel


class Provider(StrEnum):
    GOOGLE = auto()
    FAKE = auto()


class GoogleModelName(StrEnum):
    """https://ai.google.dev/gemini-api/docs/models/gemini"""

    GEMINI_15_FLASH = "gemini-1.5-flash"
    GEMINI_20_FLASH = "gemini-2.0-flash"


class FakeModelName(StrEnum):
    """Fake model for testing."""

    FAKE = "fake"


AllModelEnum: TypeAlias = GoogleModelName | FakeModelName


class ClientRequest(BaseModel):
    user_email: str
    client_name: str
    client_email: str
    meeting_timestamp: str
    meeting_description: str


class FeedbackRequest(BaseModel):
    section_id: str
    is_positive: bool
    feedback_text: str
    user_email: str
    meeting_timestamp: Optional[str] = None
