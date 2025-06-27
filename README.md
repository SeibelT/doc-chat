# DOC-CHAT 🏥💬

Medical information chatbot that explains procedures in plain language.

## Quick Start

```bash
# 1. Run setup (installs everything automatically)
python setup.py

# 2. Start the app
python app.py
```

That's it! The app will open in your browser.

## What it does

- Answers medical questions about procedures (focused on endoscopy)
- Adjusts language complexity based on user needs
- Runs 100% locally - your data stays private
- Uses RAG to provide accurate information from medical PDFs

## First time setup

The `setup.py` script handles everything:
- Installs Python packages
- Installs Ollama (AI backend)
- Downloads Mistral model (~4GB)
- Downloads embedding model
- Creates vector database from PDFs

## Managing Ollama

Use `ollama_manager.py` for easy management:

```bash
# Check if Ollama is running
python ollama_manager.py status

# Start Ollama
python ollama_manager.py start

# Stop Ollama
python ollama_manager.py stop
```

Or manage manually:

```bash
# Check if running
ollama list

# Stop Ollama
pkill ollama  # Mac/Linux
taskkill /F /IM ollama.exe  # Windows

# Start manually
ollama serve
```

## Project Structure

```
DOC-CHAT/
├── app.py                              # Main Gradio interface
├── ollama_manager.py                   # Ollama management tool
├── ollama_rag_class.py                 # RAG logic
├── setup.py                            # Automated setup
├── requirements.txt                    # Python dependencies
├── README.md                           # This file
├── .gitignore                          # Git ignore file
├── App/
│   └── rag/
│       ├── assets/                     # Additional assets
│       ├── faiss_index/                # Vector database
│       ├── create_vector_database_from_pdfs.py
│       ├── utils.py                    # Utility functions
│       └── __init__.py                 # Python package init
├── data/
│   └── pdf_1.pdf                       # Medical PDFs
└── .gitkeep                            # Git placeholder
```

## Customization

Edit `app.py` to change:
- `model_name = "mistral"` → Use different models
- `user_proficiency = "average"` → Options: "special_needs", "average", "basic_medical"

## Troubleshooting

**"Connection error"**
- Make sure Ollama is running: `ollama serve`

**"Model not found"**
- Run: `ollama pull mistral`

**Slow responses**
- Normal on first run (models loading)
- Consider GPU acceleration for faster responses

**Port already in use**
- Change port in `app.py`: `demo.launch(server_port=7861)`

## Privacy

- Everything runs locally
- No data sent to external servers
- Medical information stays on your machine