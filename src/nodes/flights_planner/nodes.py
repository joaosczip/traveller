from langchain.schema import HumanMessage, AIMessage


from .llm import llm
from .prompts import flight_search_instructions, flight_ranking_instructions
from .tools import search_flights
from ...graph.state import TravellerState, TravellerInputState, TravellerOutputState, FlightList


def flights_search_node(state: TravellerInputState):
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


def flights_ranking_node(state: TravellerState) -> TravellerOutputState:
    if state.flights is None or not len(state.flights):
        raise ValueError("No flights found to rank.")

    structured_llm = llm.with_structured_output(schema=FlightList)

    result = structured_llm.invoke(
        [
            HumanMessage(
                content=flight_ranking_instructions.format(
                    flights_list=[flight.model_dump_json() for flight in state.flights],
                )
            ),
        ]
    )

    flights_result = FlightList.model_validate(result)

    if not flights_result.flights:
        ranked_flights = sorted(
            state.flights,
            key=lambda f: (f.price, f.duration_in_minutes, f.stops),
        )

        flights_result.flights = ranked_flights[:3]

    return TravellerOutputState(
        friendly_greeting="Here are the top ranked flights based on your preferences.",
        ranked_flights=flights_result.flights,
        ranked_hotels=[],
    )
