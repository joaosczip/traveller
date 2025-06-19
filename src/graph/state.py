from pydantic import BaseModel, Field
from typing import Any

from ..models import Flight, Hotel


class TravellerInputState(BaseModel):
    trip_details: str


class TravellerState(BaseModel):
    trip_details: str
    flights: list[Flight] = Field(default_factory=list)
    ranked_flights: list[Flight] = Field(default_factory=list)
    hotels: Any
    ranked_hotels: Any
    want_hotel_search: bool = False


class FlightList(BaseModel):
    flights: list[Flight] = Field(default_factory=list)


class HotelsList(BaseModel):
    hotels: list[Hotel] = Field(default_factory=list)


class TravellerOutputState(BaseModel):
    friendly_greeting: str
    ranked_flights: list[Flight] = Field(default_factory=list)
    ranked_hotels: list[Hotel] = Field(default_factory=list)
