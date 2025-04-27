import os
from unittest.mock import patch

import pytest
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import FakeListChatModel

from currensee.core.llm import get_model
from currensee.schema.models import (
    GoogleModelName,
    FakeModelName,

)


def test_get_model_gemini():
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
        model = get_model(GoogleModelName.GEMINI_15_FLASH)
        assert isinstance(model, ChatGoogleGenerativeAI)
        assert model.model == "models/gemini-1.5-flash"
        assert model.temperature == 0.5


def test_get_model_fake():
    model = get_model(FakeModelName.FAKE)
    assert isinstance(model, FakeListChatModel)
    assert model.responses == ["This is a test response from the fake model."]


def test_get_model_invalid():
    with pytest.raises(ValueError, match="Unsupported model:"):
        # Using type: ignore since we're intentionally testing invalid input
        get_model("invalid_model")  # type: ignore