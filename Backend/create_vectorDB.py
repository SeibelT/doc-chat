import warnings
warnings.filterwarnings("ignore" )
import os
import numpy as np
import json

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.storage import InMemoryStore
from langchain.retrievers import MultiVectorRetriever

from Backend.helpers import pdf_text_extractor, pdf_table_extractor, pdf_image_extractor, create_vector_store

from pathlib import Path



def create_vectorstore_from_pdfs(pdf_dir, index_dir, chunk_size=1000, chunk_overlap=200):
    combined_text_docs = []
    combined_text_ids = []
    combined_text = []
    combined_table_docs = []
    combined_table_ids = []
    combined_tables = []

    # Load the pdf documents
    for file in os.listdir(pdf_dir):
        if not file.endswith(".pdf"):
            continue

        print(f"\n📄 Processing PDF: {file}")
        text_docs, text_ids, texts = pdf_text_extractor(pdf_dir, file)
        combined_text.extend(texts)
        combined_text_ids.extend(text_ids)
        combined_text_docs.extend(text_docs)

        # table_docs, table_ids, tables = pdf_table_extractor(model, pdf_dir, file)
        # combined_tables.extend(tables)
        # combined_table_ids.extend(table_ids)
        # combined_table_docs.extend(table_docs)

        #images = pdf_image_extractor(pdf_dir,file, output_dir="/Users/NithishChowdary1/Desktop/Workspace/Innovate-a-thon/doc-chat/data/Images")
        #all_docs_images.extend(images)

        print("completed")
        print("Succesfully loaded pdf doccument")

    print(f"Loaded available pdf documents")
    all_docs = combined_table_docs + combined_text_docs

    # Embed the chunks into vector stores
    print("\nCreating an embedding model\n")
    embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")

    vectorstore = create_vector_store(embeddings_model=embedding, n_list=5)
    docstore = InMemoryStore()

    retriever = MultiVectorRetriever(
        vectorstore = vectorstore,
        docstore = docstore,
        id_key="doc_id"
    )
    embeddings = embedding.embed_documents([doc.page_content for doc in all_docs])
    embeddings = np.array(embeddings).astype("float32")
    retriever.vectorstore.index.train(embeddings)
    retriever.vectorstore.index.nprobe = 2

    retriever.vectorstore.add_documents(combined_text_docs)
    retriever.docstore.mset(list(zip(combined_text_ids, combined_text)))


    # Save the vector store for later use
    if index_dir:
        retriever.vectorstore.save_local(index_dir)
        print(f"Vector store saved to: {index_dir}")

        # doc_dict = dict(zip(combined_text_ids + combined_table_ids, combined_text + combined_tables))
        # with open(os.path.join(index_dir, "docstore_proto.json"), "w") as f:
        #     json.dump(doc_dict, f)

# if __name__ == "__main__":
#
#     ROOT_DIR = Path(__file__).resolve().parents[2]
#     DATA_DIR = os.path.join(ROOT_DIR, "doc-chat/data")
#     INDEX_DIR = "faiss_index"
#
#     create_vectorstore_from_pdfs(str(DATA_DIR), INDEX_DIR)




