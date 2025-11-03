from langgraph.graph import StateGraph, MessagesState, START, END
import google.generativeai as genai
from langchain.schema import AIMessage
import os
from dotenv import load_dotenv
load_dotenv()
# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def gemini_llm(state: MessagesState):
    # Access latest user message (HumanMessage object)
    user_message = state["messages"][-1].content

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(user_message)
    
    text_output = response.text.strip()


    # Return as AI message
    return {"messages": [AIMessage(content=text_output)]}


graph = StateGraph(MessagesState)
graph.add_node(gemini_llm)
graph.add_edge(START, "gemini_llm")
graph.add_edge("gemini_llm", END)
graph = graph.compile()

# Step 4: Invoke the graph
result = graph.invoke({"messages": [{"role": "user", "content": "Explain LangGraph in one sentence"}]})

# Step 5: Print the output clearly
print("==== MODEL OUTPUT ====")
for msg in result["messages"]:
    print(f"{msg.type.upper()}: {msg.content}")



