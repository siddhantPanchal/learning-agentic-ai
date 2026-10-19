import math
from typing import Callable

import requests
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt.tool_node import ToolCallRequest

from todo import *


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


@tool
def rectangle_area(length: float, width: float) -> float:
    """ Return the area of a rectangle

    Only call when user asks for rectangle area or square area

    Args:
        length (float): The length of the rectangle
        width (float): The width of the rectangle

    Returns:
        float: The area of the rectangle

    """
    # await asyncio.sleep(1)
    return length * width


@tool
def circle_area(radius: float) -> str | float | int:
    """ Return the area of a circle

    Only call when user asks for circle area

    Args:
        radius (float): The radius of the circle

    Returns:
        str|float: The area of the circle if successfully calculated else returns the error message

    """
    if radius < 6:
        return "Invalid radius : {0}".format(radius)
    return 2 * math.pi * radius


@tool
def get_todo(todo_id: int) -> TodoSchema | str:
    """ Return a TodoSchema corresponding to the given id

    Only call when user asks for todo

    Args:
        todo_id (int): The id of Todo to return

    Returns:
        TodoSchema|str: The TodoSchema corresponding to the given id if successfully found else returns the error message

    """
    for todo in todos:
        if todo.id == todo_id:
            return todo
    raise Exception("Unable to find todo with requested id")
    return "Unable to find todo with requested id"


@tool
def get_weather_by_city(city: str) -> str:
    """ Return a Weather explanation string corresponding to the given city

    Only call when user asks for weather of city

    Args:
        city (str): The city to return

    Returns:
        Weather (str): The string explaining the weather of the given city

    """
    city = city.lower()
    # return f"It's always sunny in {city}! with 35 degrees."
    if city in ["london", "mumbai"]:
        return f"It's always sunny in {city}! with 35 degrees."
    else:
        mock_response = requests.Response()
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_response._content = b'{"error": "500 Internal Server Error"}'
        mock_response.raise_for_status()
        return mock_response.text
        # return "error while getting the weather data from server"
