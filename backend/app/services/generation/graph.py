from langgraph.graph import END, START, StateGraph

from app.schemas.generation import GenerationState
from app.services.generation.assemble import assemble_node
from app.services.generation.generate import generate_paper_node
from app.services.generation.plan import plan_slots_node
from app.services.generation.retrieve import attach_context_node


def build_generation_graph():
    builder = StateGraph(GenerationState)
    builder.add_node("plan_slots", plan_slots_node)
    builder.add_node("attach_context", attach_context_node)
    builder.add_node("generate_paper", generate_paper_node)
    builder.add_node("assemble", assemble_node)

    builder.add_edge(START, "plan_slots")
    builder.add_edge("plan_slots", "attach_context")
    builder.add_edge("attach_context", "generate_paper")
    builder.add_edge("generate_paper", "assemble")
    builder.add_edge("assemble", END)
    return builder.compile()


generation_graph = build_generation_graph()
