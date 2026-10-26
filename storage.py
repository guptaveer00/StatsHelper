"""One consistent local database and embedding model for Stats Helper."""
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parent


def open_collection():
    embedding = ONNXMiniLM_L6_V2()
    embedding.DOWNLOAD_PATH = ROOT / ".model_cache" / embedding.MODEL_NAME
    client = chromadb.PersistentClient(
        path=str(ROOT / "chroma_store"),
        settings=Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name="study_v2", embedding_function=embedding,
        configuration={"hnsw": {"space": "cosine"}},
    ), embedding


def full_tokenizer(embedding):
    # Use a separate tokenizer with NO truncation, so we can measure actual size.
    embedding._download_model_if_not_exists()
    path = embedding.DOWNLOAD_PATH / embedding.EXTRACTED_FOLDER_NAME / "tokenizer.json"
    tokenizer = Tokenizer.from_file(str(path))
    tokenizer.no_truncation()
    tokenizer.no_padding()
    return tokenizer


def split_to_fit(text, tokenizer, budget=230):
    """Split at word boundaries, leaving room under the model's 256-token limit."""
    current = []
    for word in text.split():
        candidate = " ".join(current + [word])
        if len(tokenizer.encode(candidate).ids) > budget:
            if current:
                yield " ".join(current)
            current = [word]
            if len(tokenizer.encode(word).ids) > budget:
                raise ValueError("A single word exceeds the embedding token budget.")
        else:
            current.append(word)
    if current:
        yield " ".join(current)
