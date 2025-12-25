import sys
from dotenv import load_dotenv
from src.graph import app
from src.utils.logger import get_logger

# Load environment variables immediately
load_dotenv()

logger = get_logger("MAIN_CONTROL")

def print_banner():
    print(r"""
    ========================================================================
       Q U A N T U M   G R A V I T Y   A G E N T   ( Q G A )   v 0 . 3
       "The Digital Einstein" | Powered by Gemini 3 & LangGraph
    ========================================================================
    """)

def run_simulation(objective: str):
    print_banner()
    logger.info(f"Initializing Research Objective: {objective}")

    # 1. Initialize the Global Blackboard (State)
    initial_state = {
        "research_objective": objective,
        "current_hypothesis": {
            "status": "NEW",
            "iteration_count": 0,
            "content": "Initial state",
            # We initialize these as None/Empty to prevent key errors later
            "title": "Pending...",
            "description": "",
            "mathematical_formulation": "",
            "simulation_data": {}
        },
        "messages": [],
        "literature_context": "" # Start empty to trigger Archivist
    }

    # 2. Execute the Cognitive Architecture
    # We set recursion_limit to 15. This allows:
    # Architect -> Archivist -> Architect -> Formalist -> Architect -> Simulator -> Architect -> Critic -> Architect -> END
    config = {"recursion_limit": 15}

    try:
        final_state = app.invoke(initial_state, config=config)
        print_report(final_state)

    except Exception as e:
        # LangGraph raises a specific error when it hits the limit. 
        # In a continuous agent loop, this is often expected behavior.
        if "recursion limit" in str(e).lower():
            logger.warning("Max recursion depth reached. The agents are taking a break.")
            # We can still print the state even if it errored out, 
            # but usually, we want to catch the last valid state. 
            # For this script, we'll just acknowledge the stop.
        else:
            logger.error(f"Critical System Failure: {e}")
            raise e

def print_report(state):
    """
    Generates a structured summary of the run.
    """
    hyp = state["current_hypothesis"]
    
    print("\n\n")
    print("="*60)
    print(f"🔬 MISSION REPORT: {hyp.get('title', 'Untitled')}")
    print("="*60)
    print(f"STATUS:      {hyp.get('status', 'UNKNOWN')}")
    print(f"CONFIDENCE:  {hyp.get('confidence_score', 'N/A')}")
    print("-" * 60)
    print(f"MATH FORMULA:\n{hyp.get('mathematical_formulation', 'N/A')}")
    print("-" * 60)
    
    sim_data = hyp.get("simulation_data", {})
    if "data" in sim_data:
        points = len(sim_data["data"])
        print(f"COMPUTATION: Successfully generated {points} topological data points.")
        print(f"DATA SAMPLE: {str(sim_data['data'])[:100]} ...")
    elif "error" in sim_data:
        print(f"COMPUTATION FAILED: {sim_data['error']}")
    else:
        print("COMPUTATION: No simulation data found.")
        
    print("="*60)
    print("\n")

if __name__ == "__main__":
    # You can pass an objective via command line, or use the default
    default_objective = "Develop a toy model for Discrete Quantum Gravity using Spin Foams"
    
    if len(sys.argv) > 1:
        user_objective = " ".join(sys.argv[1:])
    else:
        user_objective = default_objective
        
    run_simulation(user_objective)