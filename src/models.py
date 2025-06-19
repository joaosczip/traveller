from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class Flight(BaseModel):
    from_airport: str
    to_airport: str
    departure_date: datetime
    airline: str
    price: Decimal
    currency: str = "USD"
    stops: int
    duration_in_minutes: int


class Hotel(BaseModel):
    name: str
    address: str
    check_in_date: str
    check_out_date: str
    price_per_night: Decimal
    total_price: Decimal
    currency: str = "USD"
    rating: float
