from typing import Callable

from deepagents import create_deep_agent, FilesystemPermission
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import wrap_tool_call
from langchain.chat_models import init_chat_model
from langchain_core.messages import ToolMessage
from langchain_protocol import Command
from langgraph.checkpoint.memory import InMemorySaver
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
    except Exception as e:
        # Prevents the node from crashing by returning a clean ToolMessage error payload
        print(f"Intercepted exception from tool: {e}")
        return ToolMessage(
            content=f"Tool error occurred: {str(e)}. Please correct your parameters or explain the failure.",
            tool_call_id=request.tool_call["id"],
            name=request.tool_call["name"]
        )


model = init_chat_model(
    model="gemma4:e4b",
    # model="LiquidAI/lfm2.5-350m",
    model_provider="ollama",
    timeout=10
)

agent = create_deep_agent(
    model=model,
    tools=[list_directory_tool],
    backend=FilesystemBackend(root_dir="."),
    middleware=[handle_tool_errors],
    permissions=[
        # FilesystemPermission(
        #     operations=["read", "write"],
        #     paths=["/workspace/**"],
        #     mode="allow",
        # ),
        FilesystemPermission(
            operations=["read", "write"],
            paths=["/**"],
            mode="interrupt",
        ),
        # FilesystemPermission(
        #     operations=["write"],  # w,del
        #     paths=["/**/"],
        #     mode="deny",
        # ),
    ],
    checkpointer=InMemorySaver(),
    system_prompt="You are a helpful AI agent. you will help user to do some file related operations. ",
    # interrupt_on={
    #     "read_file": True,  # Default: approve, edit, reject, respond
    #     # "fetch_file": False,  # No interrupts needed
    #     # "notify_email": {"allowed_decisions": ["approve", "reject"]},  # No editing
    # },
    # "Output the tool error exactly as tool error if only occurred"
    # "STRICT SYSTEM RULE: remove / of any file name if appeared then provide to tool call"
    # "NEVER output absolute Windows paths (e.g., E:\\...). "
    # "Always use virtual Unix-style paths starting with '/' (e.g., '/file.txt').",

)


def main():
    # create new file in current dir named file.txt with 'my name is allen' content
    # create new file in E:/python/learning-agentic-ai/02/tool_permissions named file.txt with 'my name is allen' content
    # read file /E:/python/learning-agentic-ai/02/tool_permissions named file.txt
    # read file.txt
    # if not found then create new file and add some random sentence

    # print(read_file_tool(path="C:/Users/pc/projects/file.txt"))
    # write_file_tool(path="C:/Users/pc/projects/file.txt", content="my name is allen")
    print(read_file_tool(path="./file.txt"))
    query = input("User> ")
    config = {"configurable": {"recursion_limit": 6, "thread_id": 6}}
    # query = "read file.txt"
    # query = "list the directories"

    inputs = {"messages": []}

    while query != "exit":
        inputs = {"messages": inputs["messages"] + [{"role": "user", "content": query}]}
        result = agent.invoke(inputs, config=config)

        if result.get("__interrupt__"):
            # Extract interrupt information
            interrupt_value = result["__interrupt__"][0].value
            action_requests = interrupt_value["action_requests"]
            review_configs = interrupt_value["review_configs"]

            # Create a lookup map from tool name to review config
            config_map = {cfg["action_name"]: cfg for cfg in review_configs}

            # Display the pending actions to the user
            for action in action_requests:
                review_config = config_map[action["name"]]
                print(f"Tool: {action['name']}")
                print(f"Arguments: {action['args']}")
                print(f"Allowed decisions: {review_config['allowed_decisions']}")

            # Get user decisions (one per action_request, in order)
            decisions = [
                {
                    "type": "reject",
                    "message": "User rejected deleting temp.txt. Do not retry deletion.",
                }
            ]

            # Resume execution with decisions
            result = agent.invoke(
                Command(resume={"decisions": decisions}),
                config=config  # Must use the same config!
            )

        # Update messages history with all intermediate messages produced
        inputs["messages"] = result["messages"]
        # print(f"Agent> {result['messages']}")
        print(f"Agent> {result['messages'][-1].content}")
        query = input("User> ")


if __name__ == '__main__':
    main()
