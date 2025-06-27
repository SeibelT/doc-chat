# DOC-CHAT 🏥💬

Medical information chatbot that explains procedures in plain language.

## Quick Start

### Option 1: Docker (Recommended) 🐳

First, install Docker:
- **Windows/Mac**: Go to https://www.docker.com/products/docker-desktop/ and download Docker Desktop
- **Ubuntu/Linux**: Follow the official guide at https://docs.docker.com/engine/install/ubuntu/

After Docker is installed:
```bash
# Run DOC-CHAT
docker compose up
```

That's it! Docker handles everything automatically. Open your browser to the URL shown in the terminal.

### Option 2: Manual Setup

```bash
# 1. Run setup (installs everything automatically)
python setup.py

# 2. Start the app
python app.py
```

## What it does

- Answers medical questions about procedures 
- Adjusts language complexity based on user needs
- Runs 100% locally - your data stays private
- Uses RAG to provide accurate information from medical PDFs

## Docker Setup Details

Docker is the easiest way to run DOC-CHAT. It automatically:
- Creates an isolated environment
- Installs Python and all dependencies
- Installs and configures Ollama
- Downloads AI models (~4GB)
- Sets up the vector database
- No manual installation needed!

### Docker Commands

```bash
# Start the app
docker compose up

# Run in background
docker compose up -d

# Stop the app
docker compose down

# View logs
docker compose logs -f

# Update after code changes
docker compose up --build
```

## Manual Setup Details

If not using Docker, the `setup.py` script handles:
- Installing Python packages
- Installing Ollama (AI backend)
- Downloading Mistral model (~4GB)
- Downloading embedding model
- Creating vector database from PDFs

### Managing Ollama (Manual Setup Only)

Use `ollama_manager.py` for easy management:

```bash
# Check if Ollama is running
python ollama_manager.py status

# Start Ollama
python ollama_manager.py start

# Stop Ollama
python ollama_manager.py stop
```

## Project Structure

```
DOC-CHAT/
├── app.py                              # Main Gradio interface
├── ollama_manager.py                   # Ollama management tool
├── setup.py                            # Automated setup
├── requirements.txt                    # Python dependencies
├── Dockerfile                          # Docker configuration
├── docker-compose.yml                  # Docker compose config
├── .dockerignore                       # Docker ignore file
├── README.md                           # This file
├── .gitignore                          # Git ignore file
├── App/
│   └── rag/
│       ├── assets/                     # Additional assets
│       ├── faiss_index/                # Vector database
│       ├── create_vector_database_from_pdfs.py
│       ├── utils.py                    # Utility functions
│       ├── ollama_rag_class.py                 # RAG logic
│       └── __init__.py                 # Python package init
├── data/
│   └── pdf_1.pdf                       # Medical PDFs
└── .gitkeep                            # Git placeholder
```

## Privacy

- Everything runs locally
- No data sent to external servers
- Medical information stays on your machine
- Docker provides additional isolation