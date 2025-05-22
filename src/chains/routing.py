from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

from ..llms.translator import translator_chain
from ..llms.currency_converter import currency_converter_chain
from ..llms.flights_seacher import search_flights_chain

routing_chain = (
    ChatPromptTemplate.from_template(
        """
        ### Instructions
        Given the traveller input, you must classify whether they want to one of the following actions to be performerd:
            - translate a text from one language to another
            - convert money exchange rates from one currency to another
            - search for flights from one airport to another

        - When the traveller wants to translate, answer with "translation".
        - When the traveller wants to convert money exchange rates, answer with "currency_converter".
        - When the traveller wants to search for flights, answer with "search_flights".

        Always respond with a single word, and do not add any other information.\n
        Do not answer with anything else, just the classification.\n

        ### Examples
        [Traveller input]
        Eu quero uma cerveja, por favor
        [Classification]
        translation

        [Traveller input]
        54.2 EUR
        [Classification]
        currency_converter

        [Traveller input]
        Me empresta um dinheiro ai?
        [Classification]
        translation

        [Traveller input]
        I want to search for flights from CWB to GRU on March 1st, 2024.
        [Classification]
        search_flights

        Traveller input: {input}
        Classification:
    """
    )
    | ChatOllama(model="gemma3:12b")
    | StrOutputParser()
)


def invoke_chain(input):
    classification = input["classification"]
    if "translation" in classification:
        return translator_chain
    elif "currency_converter" in classification:
        return currency_converter_chain
    elif "search_flights" in classification:
        return search_flights_chain
