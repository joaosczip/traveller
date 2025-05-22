from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field
from fast_flights import FlightData, Passengers, Result as FlightResult, get_flights

from ..models import ToolCall


class FlightResponse(BaseModel):
    name: str
    is_best: bool
    price: str
    departure_date: str
    arrival_date: str
    duration: str
    stops: int


def invoke_search_flights_tool(ai_message: AIMessage) -> AIMessage:
    if not ai_message.tool_calls:
        return ai_message

    tool_calls = [
        ToolCall(
            id=tool_call["id"],
            name=tool_call["name"],
            args=tool_call["args"],
            type=tool_call.get("type"),
        )
        for tool_call in ai_message.tool_calls
    ]

    for tool_call in tool_calls:
        if tool_call.name == "_search_flights":
            from_airport = tool_call.args["from_airport"]
            to_airport = tool_call.args["to_airport"]
            departure_date = tool_call.args["departure_date"]
            return_date = tool_call.args.get("return_date")
            adults = tool_call.args.get("adults", 1)
            children = tool_call.args.get("children", 0)
            seat_type = tool_call.args.get("seat_type", "economy")
            results = tool_call.args.get("results", 3)

            flight_result = _search_flights(
                from_airport,
                to_airport,
                departure_date,
                return_date,
                adults,
                children,
                seat_type,
            )

            response_content = []
            for flight in flight_result.flights[:results]:
                flight = FlightResponse(
                    name=flight.name,
                    is_best=flight.is_best,
                    price=flight.price,
                    departure_date=flight.departure,
                    arrival_date=flight.arrival,
                    duration=flight.duration,
                    stops=flight.stops,
                )
                response_content.append(flight.model_dump())

            return AIMessage(
                content=response_content,
                tool_call_id=tool_call.id,
            )
        else:
            return AIMessage(
                content="Invalid tool call",
            )


def _search_flights(
    from_airport: str,
    to_airport: str,
    departure_date: str,
    return_date: str | None = None,
    adults: int = 1,
    children: int = 0,
    seat_type: str = "economy",
) -> FlightResult:
    """
    Search for flights using the fast_flights package.
    """
    trip = "round-trip" if return_date else "one-way"
    flight_data = [FlightData(date=departure_date, from_airport=from_airport, to_airport=to_airport)]
    if return_date:
        flight_data.append(FlightData(date=return_date, from_airport=to_airport, to_airport=from_airport))
    passengers = Passengers(
        adults=adults,
        children=children,
    )
    return get_flights(
        flight_data=flight_data,
        trip=trip,
        seat=seat_type,
        passengers=passengers,
        fetch_mode="fallback",
    )


class search_flights(BaseModel):
    from_airport: str = Field(description="The airport code to search from.")
    to_airport: str = Field(description="The airport code to search to.")
    departure_date: str = Field(description="The date of departure. ISO 8601 format.")
    return_date: str | None = Field(description="The date of return. ISO 8601 format.", default=None)
    adults: int = Field(description="The number of adults.")
    children: int = Field(description="The number of children.", default=0)
    seat_type: str = Field(description="The type of seat.", default="economy")
    results: int | None = Field(
        description="The number of results to return. If not specified, it should always be the top 3", default=3
    )


prompt_template = ChatPromptTemplate.from_template(
    """
    You are a flight searcher. You can search for flights from one airport to another.

    Traveller input: {input}
    """,
)

llm = ChatOllama(model="qwen2.5-coder:14b")
llm_with_tools = llm.bind_tools(tools=[_search_flights])

search_flights_chain = prompt_template | llm_with_tools | RunnableLambda(invoke_search_flights_tool)
