"""
A multi-agent system where a main agent routes queries to specialized agents.
This main agent uses the calculator agent for arithmetic tasks and the current time agent for date/time queries as needed.
both agents are defined in agent_to_agents.py and they will act as tools for the main agent.
"""
from strands import Agent
from agent_to_agents import calculator_agent, current_time_providing_agent
import os
from dotenv import load_dotenv
load_dotenv()
MAIN_SYSTEM_PROMPT = """
You are an assistant that routes queries to specialized agents (tools):
- For any calculation or numeric operation → Use the calculator_agent tool
- For queries about the current date and time → Use the current_time_agent tool
- For simple questions not requiring specialized knowledge → Answer directly

Always:
1. Choose the most appropriate agent/tool based on the user's query.
2. If the query requires both agents, combine their outputs logically.
3. Provide a clear and concise answer to the user.
4. Use shared memory if available to reference previous interactions.
"""

# Strands Agents SDK allows easy integration of agent tools
orchestrator = Agent(
    system_prompt=MAIN_SYSTEM_PROMPT,
    callback_handler=None,
    tools=[calculator_agent, current_time_providing_agent]
)

# Example: E-commerce Customer Service System
customer_query = "I need to know the number of days completed from January 1, 1999 to today and also calculate 15% off on a $200 purchase."

# The orchestrator automatically determines that this requires multiple specialized agents
response = orchestrator(customer_query)
print("Customer Query:", customer_query)
print("Response:", response)
