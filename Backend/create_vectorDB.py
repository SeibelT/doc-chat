import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

from Backend.helpers import pdf_document_loader, create_vector_store

from pathlib import Path



def create_vectorstore_from_pdfs(pdf_dir, index_dir, chunk_size=1000, chunk_overlap=200):

    # Load the pdf documents
    all_docs = []
    for file in os.listdir(pdf_dir):
        if file.endswith(".pdf"):
            docs = pdf_document_loader(pdf_dir, file)
            print("Succesfully loaded pdf doccument")
            all_docs.extend(docs)
    print(f"Loaded available pdf documents")

    # Splitting the documents into smaller chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunked_docs = splitter.split_documents(all_docs)
    print(f"Chunking of the pdf doccument is completed")
    print(f"\nNumber of chunks are:{len(chunked_docs)}\n")

    # Embed the chunks into vector stores
    print("\nCreating an embedding model\n")
    embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")

    vector_store = create_vector_store(embeddings_model=embedding)
    vector_store.add_documents(chunked_docs)

    # Save the vector store for later use
    if index_dir:
        vector_store.save_local(index_dir)
        print(f"Vector store saved to: {index_dir}")

if __name__ == "__main__":
    
    ROOT_DIR = Path(__file__).resolve().parents[2]
    DATA_DIR = os.path.join(ROOT_DIR, "data")
    INDEX_DIR = "faiss_index"

    create_vectorstore_from_pdfs(str(DATA_DIR), INDEX_DIR)




