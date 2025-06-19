import re
from datetime import datetime
from decimal import Decimal


def duration_to_minutes(duration_str: str) -> int:
    """
    Converts a duration string like "1 hr 15 min" to the total number of minutes.
    Examples:
        "1 hr 15 min" -> 75
        "2 hr" -> 120
        "45 min" -> 45
    """
    hours = 0
    minutes = 0

    hr_match = re.search(r"(\d+)\s*hr", duration_str)
    min_match = re.search(r"(\d+)\s*min", duration_str)

    if hr_match:
        hours = int(hr_match.group(1))
    if min_match:
        minutes = int(min_match.group(1))

    return hours * 60 + minutes


def parse_datetime_string(date_str: str) -> datetime:
    """
    Converts a string like "11:40 AM on Tue, Jul 1" to a datetime object.
    Assumes the year is the current year if not specified.
    """
    if "," in date_str:
        parts = date_str.split(",")
        if len(parts) == 2:
            date_str = date_str + f", {datetime.now().year}"
        elif len(parts) == 3 and not parts[2].strip().isdigit():
            date_str = date_str + f", {datetime.now().year}"

    try:
        return datetime.strptime(date_str, "%I:%M %p on %a, %b %d, %Y")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%I:%M %p on %b %d, %Y")
        except ValueError as e:
            raise ValueError(f"Could not parse date string: {date_str}") from e


def parse_amount_currency(s: str) -> tuple[Decimal, str]:
    """
    Parses a string like "R$218" and returns a tuple (amount, currency).
    Example: "R$218" -> (218, "BRL")
    """

    currency_map = {"R$": "BRL", "$": "USD", "€": "EUR", "£": "GBP"}

    symbol_match = re.match(r"([^\d\s]+)", s)
    symbol = symbol_match.group(1) if symbol_match else ""

    amount_match = re.search(r"(\d+(?:[.,]\d+)?)", s)
    amount = Decimal(amount_match.group(1).replace(",", ".")) if amount_match else Decimal(0)

    currency = currency_map.get(symbol, symbol)
    return (amount, currency)
