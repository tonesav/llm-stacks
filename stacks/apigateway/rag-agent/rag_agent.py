import requests
from langchain_community.llms import Ollama

MEILI_URL = "http://meilisearch:7700"
MEILI_MASTER_KEY = "your_master_key_here"
INDEX_NAME = "rag_docs"

ollama = Ollama(model="llama3.1")

def search_bm25(query):
    headers = {"X-Meili-API-Key": MEILI_MASTER_KEY}
    payload = {"q": query, "limit": 5}
    r = requests.post(f"{MEILI_URL}/indexes/{INDEX_NAME}/search", headers=headers, json=payload)
    r.raise_for_status()
    return r.json().get("hits", [])

def embed_query(query):
    r = requests.post(
        "http://host.docker.internal:11434/api/embeddings",
        json={"model": "llama3.2", "prompt": query}
    )
    r.raise_for_status()
    return r.json()["embedding"]

def search_vector(query):
    vector = embed_query(query)
    headers = {"X-Meili-API-Key": MEILI_MASTER_KEY}
    payload = {"vector": vector, "limit": 5}
    r = requests.post(f"{MEILI_URL}/indexes/{INDEX_NAME}/search", headers=headers, json=payload)
    r.raise_for_status()
    return r.json().get("hits", [])

def rag_answer(query):
    bm25_hits = search_bm25(query)
    vector_hits = search_vector(query)

    combined = bm25_hits + vector_hits
    if not combined:
        return "No relevant RAG data found."

    context = "\n\n---\n\n".join([hit["text"] for hit in combined])

    prompt = (
        "You are a 3D printing expert.\n"
        "Use ONLY the context below to answer.\n\n"
        f"{context}\n\n"
        f"User question: {query}\n\n"
        "Answer clearly and concisely."
    )

    return ollama(prompt)
