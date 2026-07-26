from fastapi import FastAPI
from rag_agent import rag_answer
from supervisor import handle_request

app = FastAPI()

@app.get("/models")
def list_models():
    import requests
    r = requests.get("http://ollama:11434/api/tags")
    models = [m["name"] for m in r.json()["models"]]
    return {"models": models}

@app.get("/ask")
def ask(q: str, model: str | None = None):
    return {"response": handle_request(q, model_override=model)}

@app.get("/rag")
def rag(q: str):
    return {"response": rag_answer(q)}

@app.get("/crew")
def crew(q: str, model: str | None = None):
    return {"response": handle_request(q, model_override=model)}

@app.get("/status")
def status():
    return {
        "rag_agent": "running",
        "crew_agent": "running",
        "ingestion": "scheduled",
        "meilisearch": "running",
        "ollama": "native"
    }

