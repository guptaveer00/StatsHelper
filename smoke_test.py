"""Small first step: verify local embeddings and persistence across processes."""

from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2


project = Path(__file__).resolve().parent
store = project / "chroma_store"
# Keep the free model download inside this project rather than the home folder.
embedding = ONNXMiniLM_L6_V2()
embedding.DOWNLOAD_PATH = project / ".model_cache" / embedding.MODEL_NAME
client = chromadb.PersistentClient(
    path=str(store), settings=Settings(anonymized_telemetry=False)
)
collection = client.get_or_create_collection(
    name="smoke_test", embedding_function=embedding
)
print(f"Count before adding: {collection.count()}")

# A stable ID makes rerunning this smoke test safe: do not add the same item twice.
if not collection.get(ids=["smoke-1"])["ids"]:
    collection.add(
        ids=["smoke-1"],
        documents=["Independent events do not change each other's probabilities."],
        metadatas=[{"source": "AI-written smoke test, not textbook corpus"}],
    )
print(f"Count after adding: {collection.count()}")
assert collection.count() == 1
print(f"Saved locally in: {store}")
