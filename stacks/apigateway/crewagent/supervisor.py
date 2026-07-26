import sys
from langchain_community.llms import Ollama

# Make sure Python can import the RAG agent
sys.path.append("Z:/Docker/rag-agent/app")

from rag_agent import rag_answer
from crew_agent import downloader_agent
from crewai import Crew, Process, Task

# LLM used for routing decisions
router_llm = Ollama(model="llama3.1")


def route_request(user_request: str) -> str:
    """
    Decides whether the request is an ACTION (CrewAI) or KNOWLEDGE (RAG).
    """
    prompt = (
        "User request:\n"
        f"{user_request}\n\n"
        "If this is an ACTION (download, fetch, run, execute, scrape), respond only: CREW.\n"
        "If this is KNOWLEDGE (explain, recommend, analyze, summarize), respond only: RAG."
    )

    decision = router_llm(prompt).strip().upper()
    return "CREW" if "CREW" in decision else "RAG"


def handle_request(user_request: str):
    """
    Routes the request to CrewAI or RAG depending on intent.
    """
    route = route_request(user_request)

    if route == "CREW":
        task = Task(
            description=user_request,
            expected_output="Completed action or downloaded data.",
            agent=downloader_agent
        )
        crew = Crew(
            agents=[downloader_agent],
            tasks=[task],
            process=Process.sequential
        )
        return crew.kickoff()

    else:
        return rag_answer(user_request)


if __name__ == "__main__":
    print("Supervisor Agent Ready.")
    while True:
        req = input("\nWhat do you want? ")
        print("\n" + str(handle_request(req)))
