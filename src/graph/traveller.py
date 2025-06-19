from langgraph.graph import StateGraph, START, END

from .state import TravellerState, TravellerInputState, TravellerOutputState
from ..nodes.flights_planner.node import flights_search_node


def build_graph():
    builder = StateGraph(TravellerState, input=TravellerInputState, output=TravellerOutputState)

    builder.add_node(
        "flights_search_node",
        flights_search_node,
    )

    builder.add_edge(START, "flights_search_node")
    builder.add_edge("flights_search_node", END)

    return builder
