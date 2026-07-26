import requests
import json

MEILI_URL = "http://meilisearch:7700"
MEILI_MASTER_KEY = "your_master_key_here"

headers = {"X-Meili-API-Key": MEILI_MASTER_KEY}

# Export
print("Exporting rag_docs...")
r = requests.get(f"{MEILI_URL}/indexes/rag_docs/documents", headers=headers)
open("rag_docs_export.json", "w").write(json.dumps(r.json()))

print("Export complete.")
