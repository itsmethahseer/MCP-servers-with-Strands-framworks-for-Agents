from langgraph.graph import StateGraph, MessagesState, START, END
import google.generativeai as genai
from langchain.schema import AIMessage
from langchain.tools import DuckDuckGoSearchRun
import os
from dotenv import load_dotenv

# Load environment and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

search = DuckDuckGoSearchRun()

# --- Define Nodes ---

def gemini_llm(state: MessagesState):
    """Gemini node: generates an answer and routes based on confidence."""
    user_message = state["messages"][-1].content
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(user_message)
    text_output = response.text.strip()

    # Basic confidence/routing logic
    if any(keyword in user_message.lower() for keyword in ["latest", "today", "current", "news", "update"]):
        next_node = "search"
    elif "?" not in user_message or len(text_output) < 20:
        # Too short, unclear, or incomplete -> pass to human
        next_node = "human"
    else:
        next_node = "end"

    return {
        "messages": [AIMessage(content=text_output)],
        "next": next_node
    }

def web_search(state: MessagesState):
    """Perform DuckDuckGo web search."""
    user_message = state["messages"][-1].content
    result = search.run(user_message)
    return {"messages": [AIMessage(content=f"Web Search Result:\n{result}")], "next": "end"}

def human_input(state: MessagesState):
    """Ask for human input, then continue to Gemini for a generalized response."""
    user_message = state["messages"][-1].content
    print(f"⚠️ HUMAN INTERVENTION REQUIRED ⚠️\nUser said: {user_message}")
    human_response = input("👤 Human agent, please type your reply: ")

    # Append human message to the conversation
    new_messages = state["messages"] + [AIMessage(content=f"Human response: {human_response}")]
    state["messages"] = new_messages

    # Route back to Gemini for a polished/generalized answer
    next_node = "llm"
    return {"messages": new_messages, "next": next_node}



# --- Build Graph ---

graph = StateGraph(MessagesState)

graph.add_node("llm", gemini_llm)
graph.add_node("search", web_search)
graph.add_node("human", human_input)
graph.add_node("end", lambda state: {"messages": state["messages"]})

graph.add_conditional_edges(
    "llm",
    lambda output: output.get("next"),
    {
        "search": "search",
        "human": "human",
        "end": END,
    },
)

graph.add_edge(START, "llm")
graph.add_edge("search", END)
graph.add_edge("human", "llm")  # <-- loop back to LLM after human input


compiled = graph.compile()

# --- Run Graph ---
query = "berno"
result = compiled.invoke({"messages": [{"role": "user", "content": query}]})

print("\n==== FINAL OUTPUT ====")
for msg in result["messages"]:
    print(msg.content)
