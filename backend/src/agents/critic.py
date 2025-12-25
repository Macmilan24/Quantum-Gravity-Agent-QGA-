# src/agents/critic.py
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from src.llm import get_llm
from src.state import ResearchState
from src.utils.logger import get_logger

logger = get_logger("CRITIC")

class Review(BaseModel):
    decision: str = Field(..., description="One of: 'APPROVE', 'REJECT'")
    feedback: str = Field(..., description="Technical critique of the hypothesis and simulation.")
    confidence_score: float = Field(..., description="Updated confidence score (0.0 to 1.0).")

def critic_node(state: ResearchState):
    logger.info("Conducting Peer Review...")
    
    model = get_llm(role="critic")
    structured_llm = model.with_structured_output(Review)
    
    hypothesis = state["current_hypothesis"]
    
    # Sanitize data for the prompt (prevent token overflow)
    sim_summary = "No data"
    if "simulation_data" in hypothesis and "data" in hypothesis["simulation_data"]:
        count = len(hypothesis["simulation_data"]["data"])
        sim_summary = f"Generated {count} 3D points. (Data hidden)"
    elif "error" in hypothesis.get("simulation_data", {}):
        sim_summary = f"Simulation Failed: {hypothesis['simulation_data']['error']}"

    system_prompt = """You are a skeptical Nobel Prize-winning Reviewer. 
    Review the proposed Quantum Gravity hypothesis and its simulation.
    
    CRITERIA:
    1. Consistency: Do the equations match the description?
    2. Simulation Status: Did the simulation run successfully?
    3. Novelty: Is this just jargon or a real attempt at unification?
    
    DECISION LOGIC:
    - If simulation failed -> REJECT.
    - If math is vague -> REJECT.
    - If promising -> APPROVE.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """
        Hypothesis: {title}
        Math: {math}
        Simulation Status: {sim_status}
        Simulation Summary: {sim_summary}
        """)
    ])
    
    try:
        review = (prompt | structured_llm).invoke({
            "title": hypothesis.get("title", "Untitled"),
            "math": hypothesis.get("mathematical_formulation", "None"),
            "sim_status": hypothesis.get("status", "UNKNOWN"),
            "sim_summary": sim_summary
        })
        
        logger.info(f"Review Outcome: {review.decision}")
        
        # Update State
        updated_hypothesis = hypothesis.copy()
        updated_hypothesis["status"] = "REVIEWED" if review.decision == "APPROVE" else "REJECTED"
        updated_hypothesis["confidence_score"] = review.confidence_score
        updated_hypothesis["critique_notes"] = hypothesis.get("critique_notes", []) + [review.feedback]
        
        return {
            "current_hypothesis": updated_hypothesis,
            "messages": [f"Critic: {review.decision} - {review.feedback}"]
        }

    except Exception as e:
        logger.error(f"Review failed: {e}")
        return {"messages": ["Critic: System error during review."]}