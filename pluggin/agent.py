from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
import json

from model import llm
from tools import (
    navigate_to_home,
    navigate_to_patient_search,
    navigate_to_patient_detail,
    get_patient_details,
    get_current_time,
)

# --- Agent State ---
class State(TypedDict):
    messages: Annotated[list, add_messages]
    context: dict
    header: dict


# --- Agent ---
all_tools = [
    navigate_to_home,
    navigate_to_patient_search,
    navigate_to_patient_detail,
    get_patient_details,
    get_current_time,
]

# Bind tools to the LLM
llm_with_tools = llm.bind_tools(all_tools)

# Load system prompt
with open("prompts/prompt.md", "r") as f:
    prompt = f.read()

system_prompt = SystemMessage(content=prompt)


def agent_node(state: State):
    """Primary node for the agent's reasoning logic."""
    messages = [system_prompt] + state["messages"]

    # Add contextual patient info if available
    if "context" in state:
        current_patient_id = state["context"].get("current_patient_id")
        if current_patient_id:
            print("Using current patient from context:", current_patient_id)
            context_message = f"(Context: The user is viewing patient with ID: {current_patient_id})"
            if messages and isinstance(messages[-1], HumanMessage):
                messages[-1].content += f" {context_message}"

    # Invoke the model
    result = llm_with_tools.invoke(messages)
    return {"messages": [result]}


# --- Graph Definition ---
graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(all_tools))

graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    lambda state: "tools" if state["messages"][-1].tool_calls else END,
)
graph.add_edge("tools", "agent")

# Compile the graph
runnable = graph.compile()


# --- Message Conversion Utilities ---
def convert_messages_to_langchain_format(messages: list[dict]) -> list:
    """Converts plain dict messages to LangChain message objects."""
    langchain_messages = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            langchain_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            tool_calls = msg.get("tool_calls")
            if tool_calls:
                langchain_messages.append(AIMessage(content=content, tool_calls=tool_calls))
            else:
                langchain_messages.append(AIMessage(content=content))
        elif role == "tool":
            langchain_messages.append(
                ToolMessage(content=content, tool_call_id=msg.get("tool_call_id"))
            )
    return langchain_messages


def serialize_messages(messages) -> list[dict]:
    """Serializes LangChain messages into JSON-safe dicts."""
    serialized_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            serialized_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            tool_calls = []
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    if isinstance(tc, dict):
                        tool_calls.append(tc)
                    else:
                        tool_calls.append({"name": tc.name, "args": tc.args, "id": tc.id})
            serialized_messages.append(
                {"role": "assistant", "content": msg.content, "tool_calls": tool_calls}
            )
        elif isinstance(msg, ToolMessage):
            serialized_messages.append(
                {"role": "tool", "content": msg.content, "tool_call_id": msg.tool_call_id}
            )
    return serialized_messages


# --- Agent Invocation ---
def agent_invocation(payload, header):
    """Invokes the patient assistant agent with a given payload and headers."""
    messages = convert_messages_to_langchain_format(payload.get("messages", []))

    initial_state = {
        "messages": messages,
        "header": {
            "authorization": header.get("authorization"),
            "content-type": "application/json"
        },
        "context": payload.get("context", {}),
    }

    # Execute the graph
    result = runnable.invoke(initial_state)
    updated_messages = serialize_messages(result["messages"])

    final_llm_response = result["messages"][-1].content
    last_tool_message_content = None

    # Find last tool message (skip time/debug responses)
    for msg in reversed(result["messages"]):
        if isinstance(msg, ToolMessage):
            content = msg.content
            if isinstance(content, str) and "current time" in content.lower():
                continue
            last_tool_message_content = content
            break

    # If there is no tool message → normal LLM response
    if not last_tool_message_content:
        return {
            "action": "speak",
            "response": final_llm_response,
            "messages": updated_messages,
        }

    # Try to parse tool output
    try:
        content = last_tool_message_content
        if isinstance(content, dict):
            data = content
        elif isinstance(content, str) and content.strip().startswith("{"):
            data = json.loads(content)
        else:
            print("⚠️ Tool output is not JSON, treating as plain text.")
            return {
                "action": "speak",
                "response": final_llm_response,
                "messages": updated_messages,
            }

        action = data.get("action", "speak")
        return {
            "action": action,
            "response": final_llm_response,
            "path": data.get("path"),
            "params": data.get("params"),
            "data": data.get("data"),
            "section": data.get("section"),
            "messages": updated_messages,
        }

    except (json.JSONDecodeError, TypeError) as e:
        print(f"❌ Error parsing tool output: {e}")
        print(f"Tool output was: {repr(last_tool_message_content)}")
        return {
            "action": "speak",
            "response": final_llm_response,
            "messages": updated_messages,
        }
