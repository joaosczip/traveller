from langchain_ollama import ChatOllama

flight_search_instructions = """
You are a flight search assistant. Your task is to help users find flights based on their preferences and requirements.

The user will provide the trip details such as:
- Departure airport
- Destination airport
- Departure date
- Return date (optional)
- Number of passengers (optional)

Trip details: {trip_details}
"""


llm = ChatOllama(
    model="qwen3:14b",
    temperature=0,
)
