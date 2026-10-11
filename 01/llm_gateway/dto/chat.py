import time
from typing import Literal, Any
from uuid import UUID

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import GenerationChunk, ChatGenerationChunk
from pydantic import BaseModel
from tenacity import RetryCallState


class ChatMessageRequest(BaseModel):
    prompt: str
    model_name: str
    model_provider: Literal["openai", "openrouter"]


class TokenTracker(AsyncCallbackHandler):

    def __init__(self):
        super().__init__()
        self.usage = {}
        self.start_time = time.perf_counter()
        self.prev = self.start_time
        self.each_token_time: list[float] = [0]

    async def on_retry(
            self,
            retry_state: RetryCallState,
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            **kwargs: Any,
    ) -> Any:
        self.usage = {}
        self.start_time = time.perf_counter()
        self.prev = self.start_time
        self.each_token_time: list[float] = [0]
        print("Retrying again")

    async def on_llm_new_token(
            self,
            token: str | list[str | dict[str, Any]],
            *,
            chunk: GenerationChunk | ChatGenerationChunk | None = None,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            tags: list[str] | None = None,
            **kwargs: Any,
    ) -> None:
        self.each_token_time.append(time.perf_counter() - self.prev)
        self.prev = time.perf_counter()
        pass

    async def on_llm_end(self, response, **kwargs):
        if len(response.generations) <= 0 and len(response.generations[0][0]) <= 0:
            return
        gen = response.generations[0][0]
        if gen and hasattr(gen, "message") and hasattr(gen.message, "usage_metadata"):
            self.usage.update(gen.message.usage_metadata)
            self.usage["speed"] = sum(self.each_token_time) / len(self.each_token_time)
            self.usage["TTFT"] = self.each_token_time[1]
            self.usage["TTLT"] = self.each_token_time[-1]
            self.usage["total_time"] = sum(self.each_token_time)

        print(self.usage)
# {
#   "prompt": "tell me about redis in 5 sentence.",
#   "model_provider": "openai",
#   "model_name": "gemma4:E2B",
# }
# {
#   "prompt": "write a program which performs fibanicci series upto given no",
#   "model_provider": "openai",
#   "model_name": "gemma4:E2B",
# }
# {
#   "prompt": "build a landing website for restaurant, use yellow and black colors. website should include landing page, contact, menu page, about us",
#   "model_provider": "openai",
#   "model_name": "gemma4:E2B",
# }
# {
#   "prompt": "tell me about redis in 5 sentence.",
#   "model_provider": "openrouter",
#   "model_name": "inclusionai/ling-3.1-flash",
# }
