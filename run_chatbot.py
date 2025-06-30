import warnings
warnings.filterwarnings("ignore" )
import subprocess
import importlib.util
import time
import threading
import gradio as gr

import os
import yaml
from Backend.helpers import is_model_available, pull_model
from Backend.create_vectorDB import create_vectorstore_from_pdfs
from Backend.rag_model import Ollama_RAG, dummy_model
from Frontend.frontend import ChatApp

import logging
import argparse


logging.basicConfig(
    filename="./meta_data/output/debug_log.log",
    filemode='a',  # append mode
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

logger.info("Initialization complete!")


REQUIREMENTS_FILE = "requirements.txt"

def install_missing_requirements():
    with open(REQUIREMENTS_FILE) as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    for pkg in packages:
        module_name = pkg.split("==")[0].split(">=")[0].split("<=")[0].strip()

        if importlib.util.find_spec(module_name) is None:
            print(f"Installing missing package: {pkg}")
            subprocess.check_call(["pip", "install", pkg])

def start_ollama():
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print("Error starting Ollama:", e)

def chat_fn(message, history):
    response = subprocess.check_output([
        "ollama", "run", "llama3", message
    ], text=True)
    return response

def chat_fn_rag(message, history): 
    response = rag_model.single_question(message)
    return response

def launch_gradio(model):
    #iface = gr.ChatInterface(fn=chat_fn_rag)
    #iface.launch(share=False, inbrowser=False) # change inbrowser to true to open directly 
    app = ChatApp(model)
    demo = app.build()
    demo.launch(share=False, inbrowser=False)

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web-App for doc2chat ")
    parser.add_argument("--model", type=str, required=False,default="mistral", help="Path to the configuration file.",choices=["mistral","dummy"])
    parser.add_argument('--check_missing', type = str2bool,required = False, default=True, help="check for missing packages etc. ")
    args = parser.parse_args()

    check_missing = args.check_missing 
    model_name = args.model
    is_dummy = model_name == "dummy"
    pdf_dir = "data"
    index_dir = "meta_data/faiss_index"
    path_prompts = "meta_data/prompts.yaml"
    print(check_missing, type(check_missing))
    if  check_missing: 
        # Step 1: Install missing packages
        install_missing_requirements()

    # Step 2: Start Ollama in background check if model is available
    if not is_dummy:
        threading.Thread(target=start_ollama, daemon=True).start()
        time.sleep(5)  # Wait for Ollama to start

    if check_missing: 

        if not is_dummy:
            if is_model_available(model_name):
                print(f"Model '{model_name}' is available locally.")
            else:
                print(f"Model '{model_name}' is not available locally.")
                pull_model(model_name)

        # Step 3: Check if VectorDB is created else create from documents in data directory
        if not os.path.exists("meta_data/faiss_index"):
            print("Creating vector store from PDFs...")
            create_vectorstore_from_pdfs(pdf_dir, index_dir, chunk_size=1000, chunk_overlap=200)
        else:
            print("Vector store already exists, skipping creation.")

    # Step 4: Load Prompt Dict 
    if not os.path.exists(path_prompts):
        print(f"Prompts file not found at {path_prompts}. Please ensure it exists.")    
    else:
        with open(path_prompts, 'r', encoding='cp1252') as file:
            prompts = yaml.safe_load(file)
            init_prompt = list(prompts.keys())[0]
        print("Prompts loaded successfully.",prompts.items())
        print(init_prompt)
    # Step 5: Init RAG Model
    rag_model = Ollama_RAG(init_prompt,prompts,index_dir,model_name,logger)  if not is_dummy else dummy_model()
    # Step 4: Launch Gradio app
    launch_gradio(rag_model)

