# graph.py
# 🚀 LangGraph pipeline definition for Rails → Django converter

from langgraph.graph import StateGraph, END
from state import ConversionState
from nodes import (
    planner_node,
    discovery_node,
    converter_node,
    builder_node,
    integration_node,
)

def build_graph():
    """
    Build and compile the Rails → Django conversion pipeline using LangGraph.
    Execution flow:
        planner → discovery → converter → builder → integration → END
    """

    # Initialize LangGraph with the ConversionState model as schema
    graph = StateGraph(ConversionState)

    # Register pipeline nodes (each node must expose a .run(state) method)
    graph.add_node("planner", planner_node.run)
    graph.add_node("discovery", discovery_node.run)
    graph.add_node("converter", converter_node.run)
    graph.add_node("builder", builder_node.run)
    graph.add_node("integration", integration_node.run)

    # Define the execution order of the pipeline
    graph.set_entry_point("planner")
    graph.add_edge("planner", "discovery")
    graph.add_edge("discovery", "converter")
    graph.add_edge("converter", "builder")
    graph.add_edge("builder", "integration")

    # Mark the integration node as the final stage
    graph.add_edge("integration", END)

    # Compile the stateful graph (required in LangGraph ≥ 1.0)
    return graph.compile()
