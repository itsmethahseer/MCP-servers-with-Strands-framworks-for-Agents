from strands import Agent
from dotenv import load_dotenv
import os
load_dotenv()
from strands_tools import current_time, calculator
agent = Agent(
    tools=[current_time, calculator])
response = agent("1. What is the current time?\n2. Calculate 3111696 / 74088")
print("Agent Response:\n", response)