from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from src.llm import get_llm
from src.state import ResearchState, HypothesisState
from src.utils.logger import get_logger
from src.prompts import FORMALIST_SYSTEM_PROMPT

logger = get_logger("FORMALIST")

class HypothesisSchema(BaseModel):
    title: str = Field(..., description="A formal title for the theory (e.g., 'Non-Commutative Spin Foam').")
    latex_equation: str = Field(..., description="The core equation in LaTeX format. No markdown ticks.")
    description: str = Field(..., description="A technical abstract of what this equation represents.")
    sympy_code: str = Field(..., description="Valid Python code using SymPy to define the equation.")
    confidence_score: float = Field(..., description="Self-evaluated confidence (0.0 to 1.0) based on literature alignment.")
    
def formalist_node(state: ResearchState):
    logger.info("Drafting mathematical hypothesis...")
    
    model = get_llm(role="coder")
    structured_llm = model.with_structured_output(HypothesisSchema)
    
    lit_context = state.get("literature_context", "No context provided.")
    objective = state["research_objective"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", FORMALIST_SYSTEM_PROMPT),
        ("human", """
        Research Objective: {objective}
        
        Literature Context:
        {lit_context}
        
        Generate a formal hypothesis object.
        """)
    ])
    
    try:
        result = (prompt | structured_llm).invoke({
            "objective": objective,
            "lit_context": lit_context
        })
        
        logger.info(f"Hypothesis Generated: {result.title}")
        
        new_hypothesis: HypothesisState = {
            "id": "gen_1", # In a real DB, we'd use UUIDs
            "title": result.title,
            "description": result.description,
            "mathematical_formulation": result.latex_equation,
            "confidence_score": result.confidence_score,
            "critique_notes": [], # Reset critiques for new hypothesis
            "iteration_count": state["current_hypothesis"].get("iteration_count", 0) + 1,
            "status": "DRAFT"
        }
        
        new_hypothesis["description"] += f"\n\nCODE_BLOCK:\n{result.sympy_code}"
        
        return {
            "current_hypothesis": new_hypothesis,
            "messages": [f"Formalist: Proposed hypothesis '{result.title}' with confidence {result.confidence_score}."]
        }
    except Exception as e:
        logger.error(f"Failed to genereate hypothesis: {e}")
        return {"messages": ["Formalist: Failed to generate valid hypothesis. Retrying."]}