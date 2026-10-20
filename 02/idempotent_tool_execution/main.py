from typing import Callable

from deepagents import create_deep_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.chat_models import init_chat_model
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest

from tools import *


@wrap_tool_call
def handle_tool_errors(
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage],
) -> ToolMessage:
    """Interception wrapper to convert node exceptions into data LangGraph understands."""
    try:
        # Tries running the tool
        return handler(request)
    except TransactionCreationError as e:
        print(f"Intercepted exception from tool: {e}")
        return ToolMessage(
            content=f"Tool error occurred: {str(e)}. Please verify the result of {request.tool_call['name']} tool_call by calling 'view_transaction' tool.",
            tool_call_id=request.tool_call["id"],
            name=request.tool_call["name"]
        )
    except Exception as e:
        # Prevents the node from crashing by returning a clean ToolMessage error payload
        print(f"Intercepted exception from tool: {e}")
        return ToolMessage(
            content=f"Tool error occurred: {str(e)}. Please correct your parameters or explain the failure.",
            tool_call_id=request.tool_call["id"],
            name=request.tool_call["name"]
        )


def main():
    model = init_chat_model(
        # model="LiquidAI/lfm2.5-350m",
        model="gemma4:e4b",
        model_provider="ollama", timeout=5
    )

    agent = create_deep_agent(
        model,
        system_prompt="You are a Personal Bank Manager who handles the transactions. "
                      "please make sure if transaction is successful added or not after each create_new_transaction tool call by calling 'view_transaction' tool."
        ,
        tools=[
            view_transaction,
            view_transactions,
            create_new_transaction
        ],
        middleware=[handle_tool_errors]
    )

    # show my all transactions
    # add new 10 INR credit transaction
    # show me transaction of id '1d37b4cf-3e69-40ba-aaf9-f7541b9901d6'
    query = input("User> ")
    config = {"configurable": {"recursion_limit": 6, "thread_id": str(uuid.uuid4())}}

    inputs = {"messages": []}
    while query != "exit":
        inputs = {"messages": inputs["messages"] + [{"role": "user", "content": query}]}
        result = agent.invoke(inputs, config=config)
        inputs["messages"] = result["messages"]
        # print(f"Agent> {result['messages']}")
        print(f"Agent> {result['messages'][-1].content}")
        query = input("User> ")


if __name__ == '__main__':
    main()
