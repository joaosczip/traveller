# Traveller

> **Work in Progress:** Traveller is under active development.

Traveller is a modern, AI-powered FastAPI backend application designed to assist travelers with intelligent trip planning and booking assistance. The application leverages Large Language Models (LLMs) and graph-based workflows to provide personalized travel recommendations.

## Core Features

### 🛫 **Flight Planning & Search**

- **Intelligent Flight Search**: Find flights based on natural language requests
- **Smart Ranking**: Automatically ranks flights by price, convenience, and travel time
- **Real-time Streaming**: Get live updates as the system searches and processes your request
- **Multi-airport Support**: Supports major airport codes (CWB, GRU, etc.)

### 💱 **Currency Conversion**

TODO

### 🌍 **Translation Services**

TODO

## LLM-Driven Architecture

Traveller leverages advanced AI and graph-based processing capabilities:

- **LangGraph Workflows**: Uses LangGraph to orchestrate complex, multi-step travel planning workflows with state management
- **Tool-Calling**: Dynamic invocation of specialized functions (flight search, ranking, booking) based on user intent
- **Streaming Responses**: Real-time Server-Sent Events (SSE) for live progress updates during flight searches
- **State Persistence**: Maintains conversation context and workflow state using checkpointers
- **LangChain Integration**: Built on LangChain for robust prompt engineering, output parsing, and tool orchestration

This creates an intelligent, context-aware travel assistant that can handle complex, multi-step planning requests with real-time feedback.

## Roadmap

- ✅ **Flight Search & Ranking:** Real-time flight search with intelligent ranking (Completed)
- 🚀 **WhatsApp Integration:** Fully integrate with WhatsApp for seamless communication
- 🌍 **More Languages & Currencies:** Expand support for additional languages and currencies
- 🏨 **Hotel Search:** Add hotel booking and recommendations
- 🚂 **Train & Bus Search:** Expand to other transportation modes

## Features

- **FastAPI**: High-performance Python web framework with async support for building APIs
- **LangGraph**: Advanced graph-based workflow orchestration for complex travel planning logic
- **LangChain**: Language model chains for translation, classification, and intelligent responses
- **Flight Search Integration**: Real-time flight data using fast-flights library
- **Streaming Responses**: Server-Sent Events (SSE) for real-time progress updates
- **Redis Caching**: Fast caching layer for currency rates and flight data
- **State Management**: Persistent conversation state with checkpointers
- **Dockerized Services**: Easy setup with Docker Compose for Redis and other services
- **Type Safety**: Full Pydantic models for request/response validation
- **Testing Suite**: Comprehensive pytest suite with mocking and coverage reporting

## Requirements

- Python 3.9+
- [Poetry](https://python-poetry.org/) for dependency management
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) for Redis

## Setup

1. **Clone the repository**

   ```sh
   git clone https://github.com/yourusername/traveller.git
   cd traveller
   ```

2. **Install dependencies**

   ```sh
   poetry install
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root with your API key:

   ```env
   EXCHANGE_RATE_API_KEY=your_api_key_here
   ```

4. **Start Redis with Docker Compose**

   ```sh
   make start-redis
   ```

5. **Run the application**

   ```sh
   poetry run uvicorn src.main:app --reload
   ```

## API Endpoints

### Health Check

- **GET** `/healthz` — System health status
  ```json
  { "status": "ok", "timestamp": "2025-06-20T10:30:00.000Z" }
  ```

### Trip Planning (Streaming)

- **POST** `/trip/planning` — Intelligent trip planning with real-time updates

**Request:**

```json
{
  "trip_details": "I want to travel from CWB to GRU on August 1st, 2025. I will be travelling alone"
}
```

**Response:** Server-Sent Events stream with JSON chunks:

1. **Flight Search Progress:**

```json
{
  "response": "Found 10 flights options. I will rank them and return the best options for you"
}
```

2. **Ranked Flight Results:**

```json
{
  "response": "Here are the top ranked flights based on your preferences.",
  "flights": [
    {
      "from_airport": "CWB",
      "to_airport": "GRU",
      "departure_date": "2025-08-01T05:20:00",
      "airline": "LATAM",
      "price": "155",
      "currency": "BRL",
      "stops": 0,
      "duration_in_minutes": 65
    }
  ]
}
```

## Usage Examples

### Flight Search

```bash
curl -X POST 'http://localhost:8000/trip/planning' \
  -H 'Content-Type: application/json' \
  --data-raw '{"trip_details": "I want to travel from CWB to GRU on August 1st, 2025. I will be travelling alone"}' \
  --no-buffer
```

### Streaming Response Example

The flight planning endpoint returns a streaming response. Here's how to handle it in JavaScript:

```javascript
const response = await fetch("/trip/planning", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    trip_details: "Flight from CWB to GRU on August 1st",
  }),
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { value, done } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const data = JSON.parse(chunk);

  if (data.flights) {
    console.log("Flights found:", data.flights);
  } else {
    console.log("Progress:", data.response);
  }
}
```

## Development

### Available Commands

- **Start Application**: `make start` or `poetry run uvicorn src.main:app --reload`
- **Run Tests**: `make test` (runs all tests with verbose output)
- **Test with Coverage**: `make test-coverage` (generates HTML coverage report)
- **Watch Tests**: `make test-watch` (runs tests on file changes)
- **Lint Code**: `make lint` (runs Ruff linting)
- **Start Redis**: `make start-redis` (starts Redis with Docker Compose)

### Testing

The project includes a comprehensive test suite with:

- Unit tests for all utility functions
- Integration tests for flight search workflows
- Mocked external dependencies for deterministic testing
- Coverage reporting with HTML output

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# View coverage report
open htmlcov/index.html
```

## Project Structure

```
src/
  main.py                     # FastAPI app and streaming endpoints
  config.py                   # Pydantic settings and configuration
  cache.py                    # Redis client and caching utilities
  models.py                   # Pydantic models (Flight, Hotel, etc.)
  chains/                     # LangChain chains and routing logic
    app.py                    # Main application chain
    routing.py                # Request routing and classification
  graph/                      # LangGraph workflow definitions
    traveller.py              # Main traveller graph with checkpointer
    state.py                  # Graph state models and schemas
  nodes/                      # Graph workflow nodes
    flights_planner/          # Flight planning node package
      __init__.py             # Package initialization
      tools.py                # Flight search tools and functions
      utils.py                # Utility functions for flight processing
      nodes.py                # Graph node implementations
      llm.py                  # LLM integration for flight planning
  llms/                       # LLM tools and integrations
    currency_converter.py     # Currency conversion LLM tool
    flights_searcher.py       # Flight search LLM integration
    translator.py             # Translation LLM tool
tests/                        # Test suite
  test_flight_searcher.py     # Comprehensive flight search tests
  test_main.py                # API endpoint tests
```

## Technical Notes

### Flight Search

- Uses the `fast-flights` library for real-time flight data
- Implements intelligent ranking based on price, duration, and convenience
- Results are limited to top 10 options for optimal user experience
- Supports major airport codes and flexible date parsing

### Caching Strategy

- Currency exchange rates cached in Redis for 1 hour
- Flight search results cached for performance optimization
- Async Redis operations for non-blocking performance

### Streaming Architecture

- Uses Server-Sent Events (SSE) for real-time updates
- Maintains workflow state with LangGraph checkpointers
- Supports multiple concurrent sessions with unique thread IDs
- Graceful error handling with retry mechanisms

### Performance

- Fully async architecture for maximum throughput
- Connection pooling for database and external API calls
- Efficient JSON serialization with Pydantic models
- Optimized graph execution with parallel node processing

### Security

- Input validation with Pydantic models
- Rate limiting ready (configurable)
- Environment-based configuration for sensitive data
- CORS headers configured for web client integration
