from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.nodes.flights_planner.utils import parse_amount_currency, duration_to_minutes, parse_datetime_string
from src.nodes.flights_planner.tools import search_flights


class TestSearchFlights:
    """Test cases for the search_flights function."""

    @patch("src.nodes.flights_planner.tools.get_flights")
    def test_search_flights_return_multiple_found_flights(self, mock_get_flights):
        """Test flight search with multiple results."""

        mock_flight1 = MagicMock()
        mock_flight1.price = "R$500"
        mock_flight1.departure = "8:15 AM on Tue, Aug 1, 2024"
        mock_flight1.name = "LATAM"
        mock_flight1.stops = 0
        mock_flight1.duration = "3 hr 20 min"

        mock_flight2 = MagicMock()
        mock_flight2.price = "€320"
        mock_flight2.departure = "2:45 PM on Tue, Aug 1, 2024"
        mock_flight2.name = "TAP Air Portugal"
        mock_flight2.stops = 2
        mock_flight2.duration = "5 hr"

        mock_result = MagicMock()
        mock_result.flights = [mock_flight1, mock_flight2]
        mock_get_flights.return_value = mock_result

        result = search_flights.invoke({"from_airport": "GRU", "to_airport": "LIS", "departure_date": "2024-08-01"})

        assert len(result) == 2

        flight1 = result[0]
        assert flight1.from_airport == "GRU"
        assert flight1.to_airport == "LIS"
        assert flight1.departure_date == datetime(2024, 8, 1, 8, 15)
        assert flight1.airline == "LATAM"
        assert flight1.price == Decimal("500")
        assert flight1.currency == "BRL"
        assert flight1.stops == 0
        assert flight1.duration_in_minutes == 200

        flight2 = result[1]
        assert flight2.departure_date == datetime(2024, 8, 1, 14, 45)
        assert flight2.airline == "TAP Air Portugal"
        assert flight2.price == Decimal("320")
        assert flight2.currency == "EUR"
        assert flight2.stops == 2
        assert flight2.duration_in_minutes == 300

    @patch("src.nodes.flights_planner.tools.get_flights")
    def test_search_flights_limits_to_10_results(self, mock_get_flights):
        """Test that search_flights limits results to 10 flights."""

        mock_flights = []
        for i in range(15):
            mock_flight = MagicMock()
            mock_flight.price = f"${100 + i * 10}"
            mock_flight.departure = f"10:00 AM on Mon, Jul {i + 1}, 2024"
            mock_flight.name = f"Airline {i + 1}"
            mock_flight.stops = i % 3
            mock_flight.duration = f"{i + 1} hr"
            mock_flights.append(mock_flight)

        mock_result = MagicMock()
        mock_result.flights = mock_flights
        mock_get_flights.return_value = mock_result

        result = search_flights.invoke({"from_airport": "JFK", "to_airport": "LAX", "departure_date": "2024-07-01"})

        assert len(result) == 10
        assert result[0].airline == "Airline 1"
        assert result[9].airline == "Airline 10"

    @patch("src.nodes.flights_planner.tools.get_flights")
    def test_search_flights_empty_results(self, mock_get_flights):
        """Test flight search with no results."""
        mock_result = MagicMock()
        mock_result.flights = []
        mock_get_flights.return_value = mock_result

        result = search_flights.invoke({"from_airport": "ABC", "to_airport": "XYZ", "departure_date": "2024-12-25"})

        assert len(result) == 0
        assert result == []


class TestParseDatetimeString:
    """Test cases for the parse_datetime_string function."""

    def test_parse_full_date_with_year(self):
        """Test parsing full date string with year."""
        result = parse_datetime_string("11:40 AM on Tue, Jul 1, 2025")
        expected = datetime(2025, 7, 1, 11, 40)
        assert result == expected

    @patch("src.nodes.flights_planner.utils.datetime")
    def test_parse_date_without_year_adds_current_year(self, mock_datetime):
        """Test parsing date string without year adds current year."""
        mock_datetime.now.return_value = datetime(2025, 6, 18, 12, 0, 0)
        mock_datetime.strptime = datetime.strptime
        result = parse_datetime_string("11:40 AM on Tue, Jul 1")
        expected = datetime(2025, 7, 1, 11, 40)
        assert result == expected

    @patch("src.nodes.flights_planner.utils.datetime")
    def test_parse_date_with_weekday_no_year(self, mock_datetime):
        """Test parsing date string without year adds current year."""
        mock_datetime.now.return_value = datetime(2025, 6, 18, 12, 0, 0)
        mock_datetime.strptime = datetime.strptime
        result = parse_datetime_string("9:30 AM on Mon, May 5")
        expected = datetime(2025, 5, 5, 9, 30)
        assert result == expected

    def test_parse_different_times_of_day(self):
        """Test parsing different times correctly."""
        test_cases = [
            ("8:15 AM on Mon, Jan 1, 2024", datetime(2024, 1, 1, 8, 15)),
            ("3:45 PM on Tue, Dec 25, 2024", datetime(2024, 12, 25, 15, 45)),
            ("12:00 PM on Wed, Jun 15, 2024", datetime(2024, 6, 15, 12, 0)),
            ("12:00 AM on Thu, Jun 15, 2024", datetime(2024, 6, 15, 0, 0)),
        ]

        for date_str, expected in test_cases:
            result = parse_datetime_string(date_str)
            assert result == expected, f"Failed for {date_str}"

    def test_parse_single_digit_day(self):
        """Test parsing date with single digit day."""
        result = parse_datetime_string("9:30 AM on Mon, May 5, 2024")
        expected = datetime(2024, 5, 5, 9, 30)
        assert result == expected

    def test_parse_different_weekdays(self):
        """Test parsing different weekday abbreviations."""
        test_cases = [
            ("10:00 AM on Mon, Jan 1, 2024", datetime(2024, 1, 1, 10, 0)),
            ("10:00 AM on Tue, Feb 1, 2024", datetime(2024, 2, 1, 10, 0)),
            ("10:00 AM on Wed, Mar 1, 2024", datetime(2024, 3, 1, 10, 0)),
            ("10:00 AM on Thu, Apr 1, 2024", datetime(2024, 4, 1, 10, 0)),
            ("10:00 AM on Fri, May 1, 2024", datetime(2024, 5, 1, 10, 0)),
            ("10:00 AM on Sat, Jun 1, 2024", datetime(2024, 6, 1, 10, 0)),
            ("10:00 AM on Sun, Jul 1, 2024", datetime(2024, 7, 1, 10, 0)),
        ]

        for date_str, expected in test_cases:
            result = parse_datetime_string(date_str)
            assert result == expected, f"Failed for {date_str}"

    def test_parse_invalid_date_raises_error(self):
        """Test parsing invalid date string raises ValueError."""
        import pytest

        with pytest.raises(ValueError, match="Could not parse date string"):
            parse_datetime_string("invalid date string")

    def test_parse_malformed_date_raises_error(self):
        """Test parsing malformed date string raises ValueError."""
        import pytest

        with pytest.raises(ValueError, match="Could not parse date string"):
            parse_datetime_string("25:70 XM on Invalid, Month 99, 2025")


class TestDurationToMinutes:
    """Test cases for the duration_to_minutes function."""

    def test_parse_hours_and_minutes(self):
        """Test parsing duration with both hours and minutes."""
        result = duration_to_minutes("1 hr 15 min")
        assert result == 75

    def test_parse_multiple_hours_and_minutes(self):
        """Test parsing duration with multiple hours and minutes."""
        result = duration_to_minutes("2 hr 30 min")
        assert result == 150

    def test_parse_only_hours(self):
        """Test parsing duration with only hours."""
        result = duration_to_minutes("2 hr")
        assert result == 120

    def test_parse_only_minutes(self):
        """Test parsing duration with only minutes."""
        result = duration_to_minutes("45 min")
        assert result == 45

    def test_parse_single_hour(self):
        """Test parsing duration with single hour."""
        result = duration_to_minutes("1 hr")
        assert result == 60

    def test_parse_single_minute(self):
        """Test parsing duration with single minute."""
        result = duration_to_minutes("1 min")
        assert result == 1

    def test_parse_zero_duration(self):
        """Test parsing zero duration."""
        result = duration_to_minutes("0 hr 0 min")
        assert result == 0

    def test_parse_large_duration(self):
        """Test parsing large duration."""
        result = duration_to_minutes("12 hr 45 min")
        assert result == 765

    def test_parse_no_spaces(self):
        """Test parsing duration without spaces."""
        result = duration_to_minutes("1hr 30min")
        assert result == 90

    def test_parse_extra_spaces(self):
        """Test parsing duration with extra spaces."""
        result = duration_to_minutes("2  hr  15  min")
        assert result == 135

    def test_parse_empty_string(self):
        """Test parsing empty string returns zero."""
        result = duration_to_minutes("")
        assert result == 0

    def test_parse_no_duration_keywords(self):
        """Test parsing string with no hr/min keywords returns zero."""
        result = duration_to_minutes("2 hours 30 seconds")
        assert result == 0

    def test_parse_partial_match_hours_only(self):
        """Test parsing string with only hr keyword."""
        result = duration_to_minutes("3 hr something else")
        assert result == 180

    def test_parse_partial_match_minutes_only(self):
        """Test parsing string with only min keyword."""
        result = duration_to_minutes("something 25 min")
        assert result == 25


class TestParseAmountCurrency:
    """Test cases for the parse_amount_currency function."""

    def test_parse_brl_currency(self):
        """Test parsing Brazilian Real currency."""
        amount, currency = parse_amount_currency("R$218")
        assert amount == Decimal("218")
        assert currency == "BRL"

    def test_parse_usd_currency(self):
        """Test parsing US Dollar currency."""
        amount, currency = parse_amount_currency("$150")
        assert amount == Decimal("150")
        assert currency == "USD"

    def test_parse_eur_currency(self):
        """Test parsing Euro currency."""
        amount, currency = parse_amount_currency("€99")
        assert amount == Decimal("99")
        assert currency == "EUR"

    def test_parse_gbp_currency(self):
        """Test parsing British Pound currency."""
        amount, currency = parse_amount_currency("£75")
        assert amount == Decimal("75")
        assert currency == "GBP"

    def test_parse_decimal_amount(self):
        """Test parsing decimal amounts."""
        amount, currency = parse_amount_currency("R$218.50")
        assert amount == Decimal("218.50")
        assert currency == "BRL"

    def test_parse_comma_decimal_amount(self):
        """Test parsing amounts with comma as decimal separator."""
        amount, currency = parse_amount_currency("€99,99")
        assert amount == Decimal("99.99")
        assert currency == "EUR"

    def test_parse_large_amount(self):
        """Test parsing large amounts."""
        amount, currency = parse_amount_currency("$1500")
        assert amount == Decimal("1500")
        assert currency == "USD"

    def test_parse_unknown_currency_symbol(self):
        """Test parsing unknown currency symbols."""
        amount, currency = parse_amount_currency("¥500")
        assert amount == Decimal("500")
        assert currency == "¥"

    def test_parse_no_currency_symbol(self):
        """Test parsing amount without currency symbol."""
        amount, currency = parse_amount_currency("100")
        assert amount == Decimal("100")
        assert currency == ""

    def test_parse_zero_amount(self):
        """Test parsing zero amount."""
        amount, currency = parse_amount_currency("$0")
        assert amount == Decimal("0")
        assert currency == "USD"

    def test_parse_amount_with_spaces(self):
        """Test parsing amount with spaces."""
        amount, currency = parse_amount_currency("R$ 218")
        assert amount == Decimal("218")
        assert currency == "BRL"

    def test_parse_invalid_amount_returns_zero(self):
        """Test parsing invalid amount returns zero."""
        amount, currency = parse_amount_currency("R$")
        assert amount == Decimal("0")
        assert currency == "BRL"

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        amount, currency = parse_amount_currency("")
        assert amount == Decimal("0")
        assert currency == ""
