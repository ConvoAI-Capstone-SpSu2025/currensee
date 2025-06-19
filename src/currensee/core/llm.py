from functools import cache
from typing import TypeAlias
from langchain_community.chat_models import FakeListChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from currensee.core.settings import settings
from currensee.schema.models import (
    AllModelEnum,
    FakeModelName,
    GoogleModelName,
)

_MODEL_TABLE = {
    GoogleModelName.GEMINI_15_FLASH: "gemini-1.5-flash",
    GoogleModelName.GEMINI_20_FLASH: "gemini-2.0-flash",
    FakeModelName.FAKE: "fake",
}

ModelT: TypeAlias = (
   ChatGoogleGenerativeAI 
)


class FakeToolModel(FakeListChatModel):
    def __init__(self, responses: list[str]):
        super().__init__(responses=responses)

    def bind_tools(self, tools):
        return self


@cache
def get_model(model_name: AllModelEnum, /) -> ModelT:
    # NOTE: models with streaming=True will send tokens as they are generated
    # if the /stream endpoint is called with stream_tokens=True (the default)
    api_model_name = _MODEL_TABLE.get(model_name)
    if not api_model_name:
        raise ValueError(f"Unsupported model: {model_name}")

    if model_name in GoogleModelName:
        return ChatGoogleGenerativeAI(model=api_model_name, temperature=0.5)
    if model_name in FakeModelName:
        return FakeToolModel(responses=["This is a test response from the fake model."])