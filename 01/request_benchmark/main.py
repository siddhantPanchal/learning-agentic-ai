import asyncio
import time
from typing import Any
from uuid import UUID

from dotenv import load_dotenv

load_dotenv()
from langchain_core.outputs import LLMResult

from langchain_core.callbacks import AsyncCallbackHandler

from langchain.chat_models import init_chat_model


class MonitorCallback(AsyncCallbackHandler):
    start_time = 0.0
    end_time = 0.0

    async def on_llm_start(
            self,
            serialized: dict[str, Any],
            prompts: list[str],
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            tags: list[str] | None = None,
            metadata: dict[str, Any] | None = None,
            **kwargs: Any,
    ) -> None:
        print(metadata)
        self.start_time = time.perf_counter()

    async def on_llm_end(
            self,
            response: LLMResult,
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            tags: list[str] | None = None,
            **kwargs: Any,
    ) -> None:
        usage = response.llm_output.get("token_usage", {})
        self.end_time = time.perf_counter()
        usage["latency"] = self.end_time - self.start_time
        print(usage, end="\n\n")


model = init_chat_model(
    model_provider='openai', model='gemma3:270M-F16',
    base_url="http://localhost:12434/v1",
    stream_usage=True,
).with_config(callbacks=[MonitorCallback()])


async def invoke(prompt: str) -> str:
    result = await model.ainvoke(prompt)
    return str(result.content)


async def main():
    with open("prompts.txt") as file:
        prompts = file.readlines()

    # await asyncio.gather(*[invoke(prompt) for prompt in prompts[:10]])

    for prompt in prompts:
        await invoke(prompt)


if __name__ == '__main__':
    asyncio.run(main())
