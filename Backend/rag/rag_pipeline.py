import os
from pathlib import Path

from rag_retriever import retrieve_context_from_vector_database
from reranking_algorithm import rerank_with_bge_reranker

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = os.path.join(ROOT_DIR, "data")
INDEX_DIR = os.path.join(ROOT_DIR, "Backend/rag/faiss_index")

def rag_pipeline(input_query, index="index"):

    retrieved_docs = retrieve_context_from_vector_database(input_query, index_dir=index, folder_path=INDEX_DIR)
    reranked_docs_with_scores = rerank_with_bge_reranker(input_query, retrieved_docs)

    reranked_chunks = [doc for doc, _ in reranked_docs_with_scores]

    return reranked_chunks

