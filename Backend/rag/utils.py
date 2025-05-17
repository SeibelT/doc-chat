import os
import faiss

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings


def pdf_doccument_loader(pdf_dir, file):
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







