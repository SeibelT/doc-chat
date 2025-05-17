from langchain_community.vectorstores import FAISS
from utils import embedding_model


def retrieve_context_from_vector_database(input_query, folder_path, index_dir, score_threshold_limit=0.3):

    embed_model = embedding_model()

    vector_store = FAISS.load_local(
        folder_path=folder_path,
        index_name=index_dir, embeddings=embed_model , allow_dangerous_deserialization=True
    )

    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={'score_threshold': score_threshold_limit}
    )

    result = retriever.invoke(input_query)
    print(f"retrievede")


input_query = "what are the main drugs used?"
index_dir = "index"
folder_path = "/doc-chat/Backend/rag/faiss_index"
retrieve_context_from_vector_database(input_query, folder_path, index_dir)



