from decimal import Decimal, ROUND_CEILING
from ..config import settings
import requests

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda


def fetch_rates():
    exchange_rate_api_url = f"https://api.freecurrencyapi.com/v1/latest?apikey={settings.EXCHANGE_RATE_API_KEY}"
    currencies = requests.get(exchange_rate_api_url).json()

    if "data" not in currencies:
        raise ValueError("Invalid response from the currency API")

    currencies_data = currencies["data"]

    return {
        "BRL": Decimal(currencies_data["BRL"]),
        "EUR": Decimal(currencies_data["EUR"]),
        "USD": Decimal(currencies_data["USD"]),
    }


def invoke_currency_converter_tool(response):
    if response.content and not response.tool_calls:
        return response.content

    for tool_call in response.tool_calls:
        if tool_call["name"] == "eur_to_brl_converter":
            eur_amount = tool_call["args"]["eur_amount"]
            eur_amount = Decimal(eur_amount) if isinstance(eur_amount, str) else eur_amount
            brl_amount = eur_to_brl_converter.invoke({"eur_amount": eur_amount})
            return ToolMessage(
                content=f"{eur_amount} EUR = {brl_amount} BRL",
                tool_call_id=tool_call["id"],
            )
        elif tool_call["name"] == "brl_to_eur_converter":
            brl_amount = tool_call["args"]["brl_amount"]
            brl_amount = Decimal(brl_amount) if isinstance(brl_amount, str) else brl_amount
            eur_amount = brl_to_eur_converter.invoke({"brl_amount": brl_amount})
            return ToolMessage(
                content=f"{brl_amount} BRL = {eur_amount} EUR",
                tool_call_id=tool_call["id"],
            )
        else:
            print(f"Unknown tool call: {tool_call['name']}")


@tool
def brl_to_eur_converter(brl_amount: Decimal) -> Decimal:
    """ "
    A tool to convert from BRL to EUR.
    This tool is used to convert money exchange rates from one currency to another.
    It'll receive a Decimal with the amount in BRL and return a Decimal with the amount in EUR.

    Example:
    brl_to_eur_converter(Decimal("1000"))
    """

    rates = fetch_rates()
    result = brl_amount * (rates["EUR"] / rates["BRL"])
    return result.quantize(Decimal("0.01"), rounding=ROUND_CEILING)


@tool
def eur_to_brl_converter(eur_amount: Decimal) -> Decimal:
    """ "
    A tool to convert from EUR to BRL.
    This tool is used to convert money exchange rates from one currency to another.
    It'll receive a Decimal with the amount in EUR and return a Decimal with the amount in BRL.

    Example:
    eur_to_brl_converter(Decimal("1000"))
    """

    rates = fetch_rates()
    result = eur_amount * (rates["BRL"] / rates["EUR"])
    return result.quantize(Decimal("0.01"), rounding=ROUND_CEILING)


prompt_template = ChatPromptTemplate.from_template(
    """"
        ### Context
        You are a helpful travelling assistant whose main goal is to help the traveller converting money exchange rates
        from one currency to another.

        You are able to convert from BRL to EUR, and vice-versa.

        If the traveller inputs a currency that is not BRL or EUR,
        you must explain them that you are only able to convert between these two currencies with a very short answer.

        Traveller amount and currency: {input}
    """,
)

tools = [
    brl_to_eur_converter,
    eur_to_brl_converter,
]


def currency_converter(model: str):
    llm = ChatOllama(model=model)

    return (
        prompt_template
        | llm.bind_tools(tools=tools)
        | RunnableLambda(invoke_currency_converter_tool)
        | StrOutputParser()
    )
