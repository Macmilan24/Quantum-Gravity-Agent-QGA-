from langgraph.graph import StateGraph, END
from src.state import ResearchState
from src.agents.architect import architect_node
from src.agents.archivist import archivist_node
from src.agents.formalist import formalist_node
from src.agents.simulator import simulator_node
from src.agents.critic import critic_node



workflow = StateGraph(ResearchState)

workflow.add_node("architect", architect_node)
workflow.add_node("archivist", archivist_node)  # Uses the real imported function
workflow.add_node("formalist", formalist_node)
workflow.add_node("simulator", simulator_node)
workflow.add_node("critic", critic_node)


def route_next(state):
    last_msg = state["messages"][-1]
    # Convert to lower case to ensure matching works
    msg_lower = last_msg.lower()

    if "archivist" in msg_lower:
        return "archivist"
    if "formalist" in msg_lower:
        return "formalist"
    if "Assigning task to simulator" in last_msg:
        return "simulator"
    if "critic" in msg_lower:
        return "critic"
    return END


workflow.set_entry_point("architect")
workflow.add_conditional_edges(
    "architect",
    route_next,
    {"archivist": "archivist", "formalist": "formalist","simulator": "simulator",  "critic": "critic"},
)

# All agents report back to the Architect
workflow.add_edge("archivist", "architect")
workflow.add_edge("formalist", "architect")
workflow.add_edge("simulator", "architect")
workflow.add_edge("critic", "architect")

# 4. Compile
app = workflow.compile()
