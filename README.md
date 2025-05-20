# Traveller

Traveller is a modern FastAPI-based backend application designed to assist travelers with two main features:

- **Currency Conversion**: Convert between BRL (Brazilian Real) and EUR (Euro) using real-time exchange rates, with smart caching for performance.
- **Translation**: Translate between Brazilian Portuguese and Spanish (Spain), with clear instructions and concise responses.

## Features

- **FastAPI**: High-performance Python web framework for building APIs.
- **LangChain**: Advanced language model chains for translation and classification.
- **Async Currency Conversion**: Uses external APIs and Redis caching for fast, up-to-date rates.
- **Dockerized Redis**: Easy setup for caching with Docker Compose.
- **Ruff & Pytest**: Linting and testing for code quality.

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

## Usage

- **Health Check**: `GET /healthz` — returns `{ "status": "ok", "timestamp": "..." }`
- **Ask a Question**: `POST /questions` with JSON body `{ "input": "your question here" }`
- **Currency Conversion**: Ask for conversions between BRL, EUR, and USD.
- **Translation**: Ask for translations between Brazilian Portuguese and Spanish (Spain).

## Development

- **Lint**: `make lint`
- **Test**: `make test`
- **Format on Save**: Enabled with Ruff in VS Code.

## Project Structure

```
src/
  main.py            # FastAPI app and endpoints
  config.py          # Pydantic settings
  cache.py           # Redis client
  chains/            # LangChain chains and routing
  llms/              # LLM tools: currency_converter, translator
  models.py          # Pydantic models
```

## Notes

- Currency rates are cached in Redis for 1 hour for performance.
- The app uses async everywhere for maximum performance.
- Make sure your API key for currency rates is valid and has quota.
