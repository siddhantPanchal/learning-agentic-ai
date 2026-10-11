from dotenv import load_dotenv, dotenv_values
from fastapi import FastAPI
from starlette.responses import StreamingResponse

load_dotenv()
from langchain_core.exceptions import ModelTimeoutError

from langchain.chat_models import init_chat_model

from dto.chat import ChatMessageRequest, TokenTracker

app = FastAPI()

models = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": dotenv_values()["OPENROUTER_API_KEY"] or "",
    },
    "openai": {
        "base_url": "http://localhost:12434/v1",
        "api_key": dotenv_values()["OPENAI_API_KEY"] or "",
    },
}

backup_model = init_chat_model(
    model_provider='openai', model='gemma4:E2B',
    base_url=models['openai']["base_url"],
    stream_usage=True,
)


@app.get("/")
async def root():
    return {"message": "Welcome to LLM Gateway", "doc_url": app.docs_url}


async def chat_handler(request: ChatMessageRequest):
    model_provider = request.model_provider
    try:
        # if model_provider == "openrouter":
        #     raise Exception("openrouter not implemented")

        model = init_chat_model(
            model_provider=model_provider, model=request.model_name,
            base_url=models[model_provider]["base_url"],
            stream_usage=True,
            # timeout=1,
        )

        model = model.with_retry(stop_after_attempt=3, wait_exponential_jitter=True)

        final_chain = model.with_fallbacks(fallbacks=[backup_model])

        res = final_chain.astream(request.prompt, config={"callbacks": [TokenTracker()]})

        async for message in res:
            text_chunk = getattr(message, "content", "")
            yield text_chunk


    except ModelTimeoutError as e:
        print(e)
        yield str({"error": str(e)})
    except Exception as e:
        print(e)
        if "not implemented" in str(e):
            # 1. Inform the client that a fallback is happening
            yield "\n[System: OpenRouter not implemented. Falling back to openai/gemma4:E2B...]\n"

            # 2. Build the fallback request payload
            fallback_request = ChatMessageRequest(
                prompt=request.prompt,
                model_provider="openai",
                model_name="gemma4:E2B"
            )

            # 3. CRITICAL: Consume and yield from the recursive fallback stream
            async for fallback_chunk in chat_handler(fallback_request):
                yield fallback_chunk
        else:
            yield str({"error": str(e)})


@app.post("/chat")
async def invoke_chat(request: ChatMessageRequest):
    print(request)
    return StreamingResponse(content=chat_handler(request), media_type="text/plain")
