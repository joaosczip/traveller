from datetime import datetime
from dateutil import parser

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field
from fast_flights import FlightData, Passengers, Result as FlightResult, get_flights

from ..models import ToolCall


def flight_date_to_datetime(date_str: str) -> datetime:
    """
    Convert a flight date string to a datetime object.
    Args:
        date_str (str): The date string in the format `3:00 PM on Sun, Jun 1` to be converted.
    Returns:
        datetime: The converted datetime object.
    """
    try:
        return parser.parse(date_str, fuzzy=True, default=None)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}")


class FlightResponse(BaseModel):
    name: str
    is_best: bool
    price: str
    departure_date: datetime
    arrival_date: datetime
    duration: str
    stops: int
    from_airport: str
    to_airport: str
    seat_type: str = "economy"
    adults: int = 1
    booking_url: str | None = None


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
                flight_response = FlightResponse(
                    name=flight.name,
                    from_airport=from_airport,
                    to_airport=to_airport,
                    is_best=flight.is_best,
                    price=flight.price,
                    departure_date=flight_date_to_datetime(flight.departure),
                    arrival_date=flight_date_to_datetime(flight.arrival),
                    duration=flight.duration,
                    stops=flight.stops,
                    adults=adults,
                )
                flight_response.booking_url = flight_response_to_url(flight_response)

                response_content.append(flight_response.model_dump())

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


def flight_response_to_url(flight: FlightResponse) -> str:
    """
    Convert a FlightResponse instance to a Booking.com flights URL.
    """
    base_url = "https://flights.booking.com/flights/"
    params = [
        "type=ONEWAY",
        f"from={flight.from_airport}",
        f"to={flight.to_airport}",
        f"cabinClass={flight.seat_type.upper()}",
        "sort=BEST",
        f"depart={flight.departure_date.date()}",
        f"adults={flight.adults}",
        "gclsrc=gf",
        "locale=en-us",
        "salesCurrency=BRL",
        "customerCurrency=BRL",
        "aid=2215358",
        "label=flights-booking-unknown",
    ]
    url = f"{base_url}{flight.from_airport}-{flight.to_airport}?{'&'.join(params)}"
    return url


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
