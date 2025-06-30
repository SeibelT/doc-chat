#!/usr/bin/env python3
"""
Docker entrypoint for DOC-CHAT
Simplified startup script that assumes Docker environment
"""
import os
import sys
import yaml
import time
import logging
from Backend.rag_model import Ollama_RAG, dummy_model
from Frontend.frontend import ChatApp
from Backend.create_vectorDB import create_vectorstore_from_pdfs

# Setup logging
logging.basicConfig(
    filename="./meta_data/output/debug_log.log",
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def wait_for_ollama(host="http://ollama:11434", max_retries=30):
    """Wait for Ollama service to be ready"""
    import requests
    
    print(f"Waiting for Ollama service at {host}...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{host}/api/tags")
            if response.status_code == 200:
                print("✓ Ollama service is ready")
                return True
        except:
            pass
        time.sleep(2)
        print(f"  Retrying... ({i+1}/{max_retries})")
    
    print("✗ Ollama service failed to start")
    return False

def ensure_model(model_name, host="http://ollama:11434"):
    """Ensure the model is available, pull if needed"""
    import requests
    
    if model_name == "dummy":
        print("Using dummy model, skipping Ollama check")
        return True
    
    # Check if model exists
    try:
        response = requests.get(f"{host}/api/tags")
        models = response.json().get('models', [])
        model_names = [m['name'] for m in models]
        
        if model_name in model_names or f"{model_name}:latest" in model_names:
            print(f"✓ Model '{model_name}' is available")
            return True
    except Exception as e:
        print(f"Error checking models: {e}")
    
    # Pull model
    print(f"Pulling model '{model_name}'...")
    try:
        response = requests.post(
            f"{host}/api/pull",
            json={"name": model_name},
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                print(f"  {line.decode('utf-8')}")
        
        print(f"✓ Model '{model_name}' pulled successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to pull model: {e}")
        return False

def main():
    # Configuration
    model_name = os.getenv('MODEL_NAME', 'mistral')
    pdf_dir = "data"
    index_dir = "meta_data/faiss_index"
    path_prompts = "meta_data/prompts.yaml"
    ollama_host = os.getenv('OLLAMA_HOST', 'http://ollama:11434')
    
    print("=" * 50)
    print("DOC-CHAT Docker Startup")
    print("=" * 50)
    print(f"Model: {model_name}")
    print(f"Ollama Host: {ollama_host}")
    
    # Wait for Ollama if not using dummy model
    if model_name != "dummy":
        if not wait_for_ollama(ollama_host):
            sys.exit(1)
        
        if not ensure_model(model_name, ollama_host):
            sys.exit(1)
    
    # Check/Create vector database
    if not os.path.exists(index_dir):
        print("\nCreating vector store from PDFs...")
        try:
            create_vectorstore_from_pdfs(pdf_dir, index_dir, chunk_size=1000, chunk_overlap=200)
            print("✓ Vector store created")
        except Exception as e:
            print(f"✗ Failed to create vector store: {e}")
            # Continue anyway - might work without it
    else:
        print("✓ Vector store already exists")
    
    # Load prompts
    if not os.path.exists(path_prompts):
        print(f"✗ Prompts file not found at {path_prompts}")
        sys.exit(1)
    
    try:
        with open(path_prompts, 'r', encoding='utf-8') as file:
            prompts = yaml.safe_load(file)
            init_prompt = list(prompts.keys())[0]
        print(f"✓ Prompts loaded: {list(prompts.keys())}")
    except Exception as e:
        print(f"✗ Failed to load prompts: {e}")
        sys.exit(1)
    
    # Initialize RAG model
    print(f"\nInitializing RAG model...")
    if model_name == "dummy":
        rag_model = dummy_model()
    else:
        # Set Ollama host for the model
        os.environ['OLLAMA_HOST'] = ollama_host
        rag_model = Ollama_RAG(init_prompt, prompts, index_dir, model_name, logger)
    
    # Launch Gradio app
    print("\nStarting Gradio interface...")
    app = ChatApp(rag_model)
    demo = app.build()
    
    # Launch with Docker-friendly settings
    demo.launch(
        server_name="0.0.0.0",  # Listen on all interfaces
        server_port=7860,
        share=False,
        inbrowser=False
    )

if __name__ == "__main__":
    main()