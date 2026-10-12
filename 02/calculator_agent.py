from dotenv import load_dotenv

load_dotenv()
from langchain.chat_models import init_chat_model

from langchain.agents import create_agent


def add(a: int | float, b: int | float) -> int | float:
    """ Add two numbers """
    return a + b


def subtract(a: int | float, b: int | float) -> int | float:
    """ Subtract two numbers """
    return a - b


def multiply(a: int | float, b: int | float) -> int | float:
    """ Multiply two numbers """
    return a * b


def divide(a: int | float, b: int | float) -> int | float:
    """ Divide two numbers """
    if b == 0:
        return 0
    return a / b


def main():
    model = init_chat_model(
        model="accounts/fireworks/models/nemotron-lightning-3p5-30b-a3b",
        model_provider="fireworks",
        # base_url="http://localhost:12434/v1"
    )

    agent = create_agent(
        model=model,
        tools=[add, subtract, multiply, divide],
        system_prompt="You are a helpful assistant",
        name="Calculator Agent",
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "what is 6 - 8 = ?"}]}
    )

    # print(result["messages"])
    print(result["messages"][-1].content_blocks)


if __name__ == '__main__':
    main()
