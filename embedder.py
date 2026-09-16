from sentence_transformers import SentenceTransformer
from typing import List

# Load a lightweight, free, open-source embedding model locally
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunks(chunks: List[str]) -> List[List[float]]:
    """Embeds chunks using a local Hugging Face model (Free & Offline)."""
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings.tolist()

def embed_User_query(query: str) -> List[float]:
    """Embeds a user query using the local model."""
    embedding = model.encode(query)
    return embedding.tolist()