from langchain.tools import tool
from fast_flights import FlightData, Passengers, get_flights
from .utils import duration_to_minutes, parse_datetime_string, parse_amount_currency

from ...models import Flight


@tool
def search_flights(
    from_airport: str,
    to_airport: str,
    departure_date: str,
) -> list[Flight]:
    """
    Search for flights using the fast_flights package.
    Args:
        from_airport (str): The IATA code of the departure airport.
        to_airport (str): The IATA code of the destination airport.
        departure_date (str): The date of departure in YYYY-MM-DD format.
    """

    flight_data = [FlightData(date=departure_date, from_airport=from_airport, to_airport=to_airport)]

    passengers = Passengers(
        adults=1,
        children=0,
    )

    result = get_flights(
        flight_data=flight_data,
        trip="one-way",
        seat="economy",
        passengers=passengers,
    )

    flights = []

    for flight in result.flights[:10]:
        amount, currency = parse_amount_currency(flight.price)

        flights.append(
            Flight(
                from_airport=from_airport,
                to_airport=to_airport,
                departure_date=parse_datetime_string(flight.departure),
                airline=flight.name,
                price=amount,
                currency=currency,
                stops=flight.stops,
                duration_in_minutes=duration_to_minutes(flight.duration),
            )
        )

    return flights
