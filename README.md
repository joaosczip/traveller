# Traveller

Traveller is a modern, LLM-driven FastAPI backend application designed to assist travelers with two main features:

- **Currency Conversion**: Convert between BRL (Brazilian Real) and EUR (Euro) using real-time exchange rates, with smart caching for performance.
- **Translation**: Translate between Brazilian Portuguese and Spanish (Spain), with clear instructions and concise responses.

## LLM-Driven Features

Traveller leverages advanced Large Language Model (LLM) capabilities, including:

- **Tool-Calling**: The app uses LLM tool-calling to dynamically invoke specialized functions (tools) for tasks like currency conversion, based on user intent.
- **Chaining**: Complex workflows are handled by chaining multiple LLM and tool calls together, enabling context-aware, multi-step reasoning and responses.
- **LangChain Integration**: Built on top of LangChain, the app orchestrates LLMs, prompt templates, output parsers, and tool routing for robust, extensible AI-driven logic.

This makes Traveller a powerful, extensible, and intelligent assistant for travelers, powered by state-of-the-art LLM technology.

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

### Example: Translation

```sh
curl -X POST 'http://localhost:8000/questions' \
  -H 'Content-Type: application/json' \
  -d '{"input": "Cerveja"}'
```

### Example: Currency Converter

```sh
curl -X POST 'http://localhost:8000/questions' \
  -H 'Content-Type: application/json' \
  -d '{"input": "54.2 EUR"}'
```

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
