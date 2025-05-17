import os
from langchain_community.vectorstores import FAISS
from utils import embedding_model
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = os.path.join(ROOT_DIR, "data")
INDEX_DIR = os.path.join(ROOT_DIR, "Backend/rag/faiss_index")

def retrieve_context_from_vector_database(input_query,  index_dir, folder_path,score_threshold_limit=0.3, no_of_documents=20):

    embed_model = embedding_model()

    vector_store = FAISS.load_local(
        folder_path=folder_path,
        index_name=index_dir, embeddings=embed_model , allow_dangerous_deserialization=True
    )

    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={'k':no_of_documents, 'score_threshold': score_threshold_limit}
    )

    retrieved_docs = retriever.invoke(input_query)

    return retrieved_docs



# input_query = "What long i have to wait after the procedure to eat?"
# index_name = "index"
# retrieve_context_from_vector_database(input_query, index_name, folder_path=INDEX_DIR)



