from dotenv import load_dotenv, dotenv_values
from langchain.chat_models import init_chat_model
from langchain_core.exceptions import ModelTimeoutError
from starlette.responses import StreamingResponse

load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

model_name = dotenv_values()["MODEL"] or ""
base_url = dotenv_values()["BASE_URL"] or ""
model = init_chat_model(
    base_url=base_url, model=model_name, model_provider="openai", timeout=4, max_retries=3,
    stream_usage=True
)


class ChatMessageRequest(BaseModel):
    prompt: str


@app.get("/")
async def root():
    return {"message": "Welcome to AI Chat!"}


async def invoke_chat(prompt: str):
    try:
        res = model.astream(prompt)
        async for message in res:
            text_chunk = getattr(message, "content", "")
            if text_chunk:
                yield text_chunk

            if hasattr(message, "usage_metadata") and message.usage_metadata:
                usage = message.usage_metadata
                prompt_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)
                print(f"\n--- Token Usage Metrics ---")
                print(f"Prompt Tokens: {prompt_tokens}")
                print(f"Completion Tokens: {output_tokens}")
                print(f"Total Tokens: {total_tokens}")

    except ModelTimeoutError as e:
        yield "The request timed out while generating a response"
    except Exception as e:
        yield f"n unexpected error occurred: {str(e)}"


@app.post("/chat")
async def chat(message: ChatMessageRequest):
    return StreamingResponse(invoke_chat(message.prompt), media_type="text/plain")
    # return {"text": res.content}
