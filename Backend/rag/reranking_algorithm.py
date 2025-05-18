import os
from pathlib import Path

import torch

from .utils import reranking_model

def rerank_with_bge_reranker(query: str, retrieved_docs: list, top_k: int = 10) -> list:
    """
    Rerank retrieved documents using BGE-Reranker-Large.

    Args:
        query (str): The original user query.
        retrieved_docs (list): List of langchain Document objects or strings.
        top_k (int): Number of top results to return after reranking.

    Returns:
        List of top-k tuples: (document, score)
    """
    # Extract text from Document objects if needed
    retrieved_content_from_chunks = [doc.page_content if hasattr(doc, "page_content") else doc for doc in retrieved_docs]

    # Format input as required by bge-reranker
    inputs = [f"query: {query} document: {doc}" for doc in retrieved_content_from_chunks]

    reranker = reranking_model(model_name="BAAI/bge-reranker-large", top_k=top_k)

    # Run through reranker
    with torch.no_grad():
        raw_scores = reranker(inputs)

        scores = [s[0]['score'] for s in raw_scores]

    # Combine with original docs
    reranked = sorted(
        zip(retrieved_content_from_chunks, scores),
        key=lambda x: x[1],
        reverse=True
    )
    print(f"Reranked the chunks successfully")

    # Return top-k
    return reranked[:top_k]

# ROOT_DIR = Path(__file__).resolve().parents[2]
# DATA_DIR = os.path.join(ROOT_DIR, "data")
# INDEX_DIR = os.path.join(ROOT_DIR, "Backend/rag/faiss_index")
#
# input_query = "What long i have to wait after the procedure to eat?"
# index_name = "index"
# retrieved_docs = retrieve_context_from_vector_database(input_query, index_name, folder_path=INDEX_DIR)
# results = rerank_with_bge_reranker("How long i have to wait after the procedure before i can eat?", retrieved_docs)
# print(results)
