import os
import uuid
import fitz
import io
import base64
import faiss
import torch
import pdfplumber

from io import BytesIO
from PIL import  Image
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from transformers import BlipProcessor, BlipForConditionalGeneration




def pdf_text_extractor(pdf_dir, file):
    document_loader = UnstructuredPDFLoader(os.path.join(pdf_dir, file), mode="elements", strategy="fast")
    docs = document_loader.load()
    current_title = ""
    current_text_group = []
    text_docs = []
    text_ids = []
    texts = []

    for i, doc in enumerate(docs):
        category = doc.metadata.get("category", "").lower()
        content = doc.page_content.strip()

        if not content:
            continue

        if category == "title":
            if current_text_group:
                text_id = str(uuid.uuid4())
                text_ids.append(text_id)
                combined = f"{current_title}\n\n" + "\n".join(current_text_group) if current_title else "\n".join(current_text_group)
                metadata = {**doc.metadata, "file_name": file, "type": "text",  "file_path": os.path.join(pdf_dir,file), "doc_id": text_id}
                texts.append(combined)
                text_docs.append(Document(
                   page_content=combined,
                    metadata=metadata
                ))
                current_text_group = []
            current_title = content

        elif category in ["narrativetext", "listitem", "uncategorizedtext"]:
            current_text_group.append(content)


    # Final flush of leftover section
    if current_text_group:
        text_id = str(uuid.uuid4())
        text_ids.append(text_id)
        combined = f"{current_title}\n\n" + "\n".join(current_text_group) if current_title else "\n".join(
            current_text_group)
        texts.append(combined)
        text_docs.append(Document(page_content=combined, metadata={"file_name": file, "type": "text", "doc_id":text_id}))

    print(f"✅ Loaded and chunked '{file}'")
    return text_docs, text_ids, texts



def pdf_table_extractor(model, pdf_dir, file):
    table_docs = []
    table_ids = []
    tables = []
    summary_chain = summarise_chain(model)
    with pdfplumber.open(os.path.join(pdf_dir, file)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):

            extracted_table = page.extract_tables()
            for t_index, table in enumerate(extracted_table):
                try:
                    table_summary = summary_chain.invoke({"element": table})
                except Exception as e:
                    table_summary = table

                text_as_html = table_to_html(table)
                tables.append(text_as_html)
                table_id = str(uuid.uuid4())
                table_ids.append(table_id)

                table_docs.append(Document(
                    page_content=table_summary,
                    metadata={
                        "type": "table",
                        "file_name": file,
                        "file_path": os.path.join(pdf_dir,file),
                        "page_num": page_num,
                        "doc_id": table_id
                    }
                ))
    return table_docs, table_ids, tables



def pdf_image_extractor(pdf_dir, file, output_dir:str):
    doc = fitz.open(os.path.join(pdf_dir,file))
    base_name = os.path.splitext(file)[0]
    image_docs = []
    image_ids = []
    images_base64 = []

    os.makedirs(output_dir, exist_ok=True)

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            try:
                image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")

                image_filename = f"{base_name}_p{page_num+1}_i{img_index+1}.{image_ext}"
                image_path = os.path.join(output_dir,image_filename)

                image_pil.save(image_path)

                image_summary = summarise_images(image_path)
                img_encoded_str = encode_image_base64(image_path)

                img_id = str(uuid.uuid4())

                image_ids.append(img_id)
                images_base64.append(img_encoded_str)

                image_docs.append(Document(
                    page_content=f"Image Summary:{image_summary}",
                    metadata={
                        "type": "image",
                        "file_name": file,
                        "page": page_num + 1,
                        "image_id": img_index + 1,
                        "image_ext": image_ext,
                        "image_path": image_path,
                        "doc_id": img_id
                    }
                ))

            except Exception as e:
                print(f"❌ Failed to load image {img_index} on page {page_num + 1}: {e}")

    return image_docs, image_ids, images_base64


def get_images_base64(chunks):
    img_base64 = []
    for chunk in chunks:
        if "CompositeElement" in str(type(chunk)):
            chunk_els = chunk.metadata.orig_elements
            for el in chunk_els:
                if "Image" in str(type(el)):
                    img_base64.append(el.metadata.image_base64)

    return img_base64

def vision_model(model_name: str = "Salesforce/blip-image-captioning-base"):
    processor = BlipProcessor.from_pretrained(model_name)
    model = BlipForConditionalGeneration.from_pretrained(model_name)

    return processor, model
def summarise_images(img):
    try:
        image = Image.open(img).convert("RGB")

        # Optional: Resize large images
        MAX_SIZE = 512
        if max(image.size) > MAX_SIZE:
            image.thumbnail((MAX_SIZE, MAX_SIZE))

        # Safe inference with no_grad
        with torch.no_grad():

            processor, model = vision_model()

            image = Image.open(img).convert("RGB")
            inputs = processor(image, return_tensors="pt")
            output = model.generate(**inputs)
            summary = processor.decode(output[0], skip_special_tokens=True)

            return summary

    except Exception as e:
        print(f"⚠️ Image summarization failed for {img}: {e}")
        return "Summary unavailable due to error."

def table_to_html(table):
    html = "<table border='1' style='border-collapse: collapse;'>\n"
    for row in table:
        html += "  <tr>\n"
        for cell in row:
            cell_content = cell if cell is not None else ""
            html += f"    <td style='padding: 4px'>{cell_content}</td>\n"
        html += "  </tr>\n"
    html += "</table>"
    return html

def encode_image_base64(img):

    with Image.open(img) as img:
        buffered = BytesIO()
        img.save(buffered,format="JPEG")
        img_str=base64.b64encode(buffered.getvalue().decode("utf-8"))
        return img_str

def chunk_doccument(doccument, chunk_size: int, chunk_overlap: int):
    text_processor = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    for doc in doccument:
        doc.page_content = doc.page_content.replace('\x00', '')

    return text_processor.split_documents(doccument)

def table_to_html(table):
    html = "<table border='1' style='border-collapse: collapse;'>\n"
    for row in table:
        html += "  <tr>\n"
        for cell in row:
            cell_content = cell if cell is not None else ""
            html += f"    <td style='padding: 4px'>{cell_content}</td>\n"
        html += "  </tr>\n"
    html += "</table>"
    return html


def create_vector_store(embeddings_model, n_list:int=50):
    dimensions = len(embeddings_model.embed_query("hello world"))
    quantizer = faiss.IndexFlatL2(dimensions)
    index = faiss.IndexIVFFlat(quantizer, dimensions,n_list, faiss.METRIC_L2 )

    vector_store = FAISS(
        embedding_function=embeddings_model,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={})

    return vector_store