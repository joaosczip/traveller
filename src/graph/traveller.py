from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .state import TravellerState, TravellerInputState, TravellerOutputState
from ..nodes.flights_planner.nodes import flights_search_node, flights_ranking_node


def build_graph():
    builder = StateGraph(TravellerState, input=TravellerInputState, output=TravellerOutputState)

    builder.add_node(
        "flights_search_node",
        flights_search_node,
    )
    builder.add_node(
        "flights_ranking_node",
        flights_ranking_node,
    )

    builder.add_edge(START, "flights_search_node")
    builder.add_edge("flights_search_node", "flights_ranking_node")
    builder.add_edge("flights_ranking_node", END)

    return builder


def compile_with_checkpointer():
    """Build the graph with a memory checkpointer for state management."""
    builder = build_graph()
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)
