import arxiv
import io
from typing import List
from pypdf import PdfReader
from langchain_core.messages import HumanMessage, SystemMessage
from src.llm import get_llm
from src.state import ResearchState
from src.utils.logger import get_logger
from src.prompts import ARCHIVIST_SYSTEM_PROMPT

logger = get_logger("ARCHIVIST")


def fetch_arxiv_paper(query: str, max_result: int = 2) -> str:
    """
    Tools: Searches ArXiv and returns text content of abstract and summary.
    """
    cleaned_query = query.replace('\\"', '"').strip('"')

    logger.info(f"Query ArXiv for: {query}")
    search = arxiv.Search(
        query=cleaned_query,
        max_results=max_result,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    context_accumulator = ""

    for result in search.results():
        logger.info(f"Found paper: {result.title}")
        context_accumulator += f"### Title: {result.title}\n"
        context_accumulator += (
            f"### Authors: {', '.join([a.name for a in result.authors])}\n"
        )
        context_accumulator += f"### Abstract: {result.summary}\n"
        context_accumulator += f"### URL: {result.pdf_url}\n\n"

    return context_accumulator


def archivist_node(state: ResearchState):
    logger.info("Analyzing research objective...")
    model = get_llm(role="researcher")

    query_gen_prompt = f"""Convert the following physics objective into a precise ArXiv search query.
    Ensure terms are correctly quoted and use 'AND' or 'OR' where appropriate for clarity.
    Objective: '{state['research_objective']}'
    
    Return ONLY the search query string. Do NOT include instructions or explanations.
    Example: "Quantum Gravity" AND "Spin Foams" AND "Toy Model"
    """
    search_query = model.invoke(query_gen_prompt).content.strip()

    raw_data = fetch_arxiv_paper(search_query)
    
    if raw_data.startswith("ERROR:"):
        logger.error(f"Failed to fetch papers: {raw_data}")
        return {"messages": [f"Archivist: {raw_data} Could not proceed with literature review."]}
    
    if not raw_data:
        logger.warning("No papers found. Retrying with broader query")
        raw_data = fetch_arxiv_paper("Quantum Gravity Reviews")

    logger.info("Synthesizing literature context...")
    synthesis_prompt = [
        SystemMessage(content=ARCHIVIST_SYSTEM_PROMPT),
        HumanMessage(
            content=f"Here is the raw data from ArXiv:\n\n{raw_data}\n\nSynthesize this for the Formalist agent."
        ),
    ]

    synthesis = model.invoke(synthesis_prompt).content

    logger.info("Literature review complete.")

    return {
        "literature_context": synthesis,
        "messages": [
            f"Archivist: Retrieved and analyzed papers on '{search_query}'. Ready for formalization."
        ],
    }
