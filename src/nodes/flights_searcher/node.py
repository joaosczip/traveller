from langchain.schema import HumanMessage, AIMessage


from .llm import llm, flight_search_instructions
from .tools import search_flights
from ...graph.state import TravellerState


def flights_search_node(state: TravellerState):
    llm_with_tools = llm.bind_tools([search_flights])

    result = llm_with_tools.invoke(
        [
            HumanMessage(
                content=flight_search_instructions.format(
                    trip_details=state.trip_details,
                )
            ),
        ]
    )

    flights = []

    if isinstance(result, AIMessage) and result.tool_calls:
        tool_call = result.tool_calls[0]
        args = tool_call["args"]
        if tool_call["name"] == "search_flights":
            flights = search_flights.invoke(
                {
                    "from_airport": args["from_airport"],
                    "to_airport": args["to_airport"],
                    "departure_date": args["departure_date"],
                }
            )

    return {"flights": flights}
