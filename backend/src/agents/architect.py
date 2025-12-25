from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from src.llm import get_llm
from src.state import ResearchState
from src.utils.logger import get_logger
from src.prompts import ARCHITECT_SYSTEM_PROMPT

logger = get_logger("ARCHITECT")


class NextMove(BaseModel):
    """
    The decision on which agent performs the next steps.
    """

    next_agent: str = Field(
        ...,
        description="One of: 'archivist', 'formalist', 'simulator', 'critic', 'human'",
    )
    reasoning: str = Field(..., description="Why we are choosing this agent.")
    instruction: str = Field(..., description="Specific instruction for the next agent")


def architect_node(state: ResearchState):
    logger.info("Deliberating next step...")

    model = get_llm(role="strict")
    structured_llm = model.with_structured_output(NextMove)

    # Check if we have context (Logic for the prompt)
    has_context = "True" if state.get("literature_context") else "False"

    hypothesis_summary = state["current_hypothesis"].copy()

    if "simulation_data" in hypothesis_summary:
        data_count = len(hypothesis_summary["simulation_data"].get("data", []))
        hypothesis_summary["simulation_data"] = (
            f"<Summary: {data_count} data points generated. Data hidden to save context.>"
        )

    if "simulation_code" in hypothesis_summary:
        hypothesis_summary["simulation_code"] = "<Code hidden to save context>"

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", ARCHITECT_SYSTEM_PROMPT),
            ("human", "Current State Context: {context}. Last messages: {messages}"),
        ]
    )

    chain = prompt | structured_llm

    try:
        decision = chain.invoke(
            {
                "objective": state["research_objective"],
                "status": state["current_hypothesis"].get("status", "NEW"),
                "iteration": state["current_hypothesis"].get("iteration_count", 0),
                "has_context": has_context,  # Passing the flag to the LLM
                "context": str(hypothesis_summary),
                "messages": state["messages"][-3:],
            }
        )
    except Exception as e:
        # Fallback if Gemini hallucinates a non-JSON
        logger.error(f"Decision parsing failed: {e}")
        return {"messages": ["Architect: Error in decision making. Retrying."]}

    logger.info(f"Decision: {decision.next_agent.upper()} -> {decision.reasoning}")

    return {
        "messages": [
            f"Architect: Assigning task to {decision.next_agent}: {decision.instruction}"
        ]
    }
