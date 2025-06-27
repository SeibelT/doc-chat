import os
import faiss

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from transformers import pipeline
import subprocess

def pdf_document_loader(pdf_dir, file):
    doccument_loader = PDFPlumberLoader(os.path.join(pdf_dir, file))
    return doccument_loader.load()


def chunk_doccument(doccument, chunk_size: int, chunk_overlap: int):
    text_processor = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    for doc in doccument:
        doc.page_content = doc.page_content.replace('\x00', '')

    return text_processor.split_documents(doccument)

def create_vector_store(embeddings_model):


    index = faiss.IndexFlatL2(len(embeddings_model.embed_query("hello world")))

    vector_store = FAISS(
        embedding_function=embeddings_model,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={})

    return vector_store


def embedding_model(model_name="BAAI/bge-large-en-v1.5"):

    return HuggingFaceEmbeddings(model_name=model_name)


def reranking_model(model_name="BAAI/bge-reranker-large", top_k=5):

    # Initialize the bge-reranker-large model once
    reranker = pipeline(
        "text-classification",
        model=model_name,
        top_k=top_k,
        device=0  # Set to 0 if using CUDA (GPU)
    )

    return  reranker




def is_model_available(model_name):
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    return model_name in result.stdout

def pull_model(model_name):
    print(f"Pulling model '{model_name}'...")
    subprocess.run(["ollama", "pull", model_name])