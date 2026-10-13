from dotenv import load_dotenv

load_dotenv()
from langchain.chat_models import init_chat_model

from langchain.agents import create_agent


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}! with 35 degrees."


def main():
    model = init_chat_model(
        # model="accounts/fireworks/models/nemotron-lightning-3p5-30b-a3b",
        model="nvidia/nemotron-3.5-lightning-30b-a3b",
        model_provider="nvidia",
        # base_url="http://localhost:12434/v1"
    )

    agent = create_agent(
        model=model,
        tools=[get_weather],
        system_prompt="You are a helpful assistant",
        name="Weather Agent",
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]}
    )

    # print(result["messages"])
    print(result["messages"][-1].content_blocks)


if __name__ == '__main__':
    main()
