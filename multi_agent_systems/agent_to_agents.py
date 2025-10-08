from strands import Agent
from strands_tools import calculator
from strands_tools import current_time

# Define Calculator Agent
calculator_agent = Agent(
    name="CalculatorAgent",
    description="Performs basic arithmetic operations.",
    tools=[calculator],
)

# Define Weather Agent
current_time_providing_agent = Agent(
    name="WeatherAgent",
    description="Provides weather information for a location.",
    tools=[current_time],
)
