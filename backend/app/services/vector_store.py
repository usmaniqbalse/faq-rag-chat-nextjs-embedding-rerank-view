import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)
from langchain_core.documents import Document
from typing import List
from ..config import settings

def get_vector_collection() -> chromadb.Collection:
    ollama_ef = OllamaEmbeddingFunction(
        url=f"{settings.OLLAMA_BASE_URL}/api/embeddings",
        model_name=settings.EMBED_MODEL,
    )
    client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
    return client.get_or_create_collection(
        name="rag_app",
        embedding_function=ollama_ef,
        metadata={"hnsw:space": "cosine"},
    )

def add_to_vector_collection(all_splits: List[Document], file_name: str) -> int:
    collection = get_vector_collection()
    docs, metas, ids = [], [], []
    for idx, split in enumerate(all_splits):
        docs.append(split.page_content)
        metas.append(split.metadata)
        ids.append(f"{file_name}_{idx}")
    collection.upsert(documents=docs, metadatas=metas, ids=ids)
    return len(ids)

def query_collection(prompt: str, n_results: int = 10):
    collection = get_vector_collection()
    return collection.query(query_texts=[prompt], n_results=n_results)
