from sentence_transformers import CrossEncoder
from typing import List, Tuple

# Rank and return top-3 concatenated text and ids
def rerank_top3(prompt: str, documents: List[str]) -> Tuple[str, List[int]]:
    relevant_text = ""
    relevant_ids: List[int] = []
    encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    ranks = encoder.rank(prompt, documents, top_k=3)
    for r in ranks:
        relevant_text += documents[r["corpus_id"]]
        relevant_ids.append(r["corpus_id"])
    return relevant_text, relevant_ids
