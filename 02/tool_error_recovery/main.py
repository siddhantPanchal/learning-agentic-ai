import asyncio

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from tools import *


async def main():
    model = init_chat_model(
        model_provider="ollama",
        model="gemma4:e4b ",
        # model="LiquidAI/lfm2.5-350m",
        timeout=3
    )

    agent = create_agent(
        model, system_prompt="You are good in calculations, Please use tools to calculate the math",
        tools=[rectangle_area, circle_area, get_todo, get_weather_by_city],
        middleware=[handle_tool_errors],
    )

    contents = [
        # "calculate the area of square with 5cm in length",
        # "calculate the area of rectangle with 5cm in width and 10cm in length",
        # "calculate the area of circle with 5cm in circle radius",
        # "calculate the area of circle with -5cm in circle radius",
        # "get my todo with id 1",
        # "get my todo with id 10",
        "get mumbai weather",
        "get london weather",
        "get patna weather",
    ]

    for content in contents:
        print(content)
        result = agent.invoke(
            {"messages": [{"role": "user", "content": content}]},
            config={"recursive_limit": 10},
        )
        print(result["messages"][-1].content, end="\n\n")


if __name__ == '__main__':
    asyncio.run(main())
