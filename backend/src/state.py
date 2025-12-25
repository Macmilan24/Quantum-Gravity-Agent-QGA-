from typing import List, Optional, Annotated
from typing_extensions import TypedDict
import operator


class HypothesisState(TypedDict):
    id: str
    title: str
    description: str
    mathematical_formulation: str
    confidence_score: float
    critique_notes: List[str]  # Peer Review comments
    iteration_count: int
    simulated_code: Optional[str] # Python code for simulation
    simulation_data: Optional[Any]
    status: str  # 'DRAFT', 'REVIEWED', 'VERIFIED'


class ResearchState(TypedDict):
    messages: Annotated[List[str], operator.add]
    current_hypothesis: HypothesisState
    literature_context: str
    research_objective: str
