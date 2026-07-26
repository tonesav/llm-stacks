from crewai.tools import Tool
from rag_agent import rag_answer  # import from your rag_agent.py

def rag_query_tool_fn(query: str) -> str:
    """Query the local RAG index for 3D printing knowledge."""
    return rag_answer(query)

rag_tool = Tool(
    name="RAG Knowledge Tool",
    description="Queries the local Meilisearch+Ollama RAG index for 3D printing answers.",
    func=rag_query_tool_fn
)
