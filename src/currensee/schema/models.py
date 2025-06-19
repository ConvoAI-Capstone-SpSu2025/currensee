from enum import StrEnum, auto
from typing import TypeAlias


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
