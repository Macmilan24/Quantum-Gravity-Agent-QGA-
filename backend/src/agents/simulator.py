import subprocess
import sys
import json
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from src.llm import get_llm
from src.state import ResearchState
from src.utils.logger import get_logger
from src.prompts import SIMULATOR_SYSTEM_PROMPT

logger = get_logger("SIMULATOR")

class SimulationCode(BaseModel):
    """Structure for the code generation"""
    python_code: str = Field(..., description="The executable Python script.")
    explanation: str = Field(..., description="Brief explanation of the mapping from math to data.")
    
def execute_simulation(code: str) -> dict:
    """
    Executes the generated code in a subprocess to get the JSON result.
    """
    logger.info("Spinning up simulation subprocess...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-c",code],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            logger.error(f"Simulation crashed: {result.stderr}")
            return {"error": result.stderr}
        output = result.stdout.strip()
        # Find the JSON part (sometimes LLMs print debug text)
        start = output.find('{')
        end = output.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = output[start:end]
            return json.loads(json_str)
        else:
            return {"error": "No JSON found in output"}
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        return {"error": str(e)}

def simulator_node(state: ResearchState):
    logger.info("Initializing Numerical Relativity Engine...")
    
    hypothesis = state["current_hypothesis"]
    
    if "mathematical_formulation" not in hypothesis:
        return {"message": ["Simulator: No math found to simulate. Aborting."]}
    
    model = get_llm(role="coder")
    structured_llm = model.with_structured_output(SimulationCode)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SIMULATOR_SYSTEM_PROMPT),
        ("human", """
        Hypothesis: {title}
        Math: {math}
        Description/Code: {desc}
        
        Generate the simulation script.
        """)
    ])
    logger.info("Generating simulation code...")
    result = (prompt | structured_llm).invoke({
        "title": hypothesis["title"],
        "math": hypothesis["mathematical_formulation"],
        "desc": hypothesis.get("description", "")
    })
    
    logger.info("Verifying code execution...")
    sim_data = execute_simulation(result.python_code)
    
    if "error" in sim_data:
        status = "SIMULATION_FAILED"
        msg = f"Simulator: Code generated but crashed: {sim_data['error'][:100]}..."
    else:
        status = "SIMULATED"
        msg = "Simulator: 3D Data successfully generated."
        logger.info(f"Generated {len(sim_data.get('data', []))} data points.")
    
    updated_hypothesis = hypothesis.copy()
    updated_hypothesis["status"] = status
    updated_hypothesis["simulated_code"] = result.python_code
    updated_hypothesis["simulation_data"] = sim_data
    
    return {
        "current_hypothesis": updated_hypothesis,
        "messages": [msg]
    }
    