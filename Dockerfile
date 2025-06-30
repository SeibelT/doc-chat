# Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p meta_data/faiss_index meta_data/output data

# Expose Gradio port
EXPOSE 7860

# Create startup script with environment variable support
RUN echo '#!/bin/bash\n\
echo "Waiting for Ollama service..."\n\
sleep 10\n\
if [ "$MODEL_NAME" != "dummy" ]; then\n\
    echo "Pulling $MODEL_NAME model..."\n\
    curl -X POST http://ollama:11434/api/pull -d "{\"name\": \"$MODEL_NAME\"}"\n\
fi\n\
echo "Downloading HuggingFace embedding model..."\n\
python -c "from langchain.embeddings import HuggingFaceEmbeddings; e = HuggingFaceEmbeddings(model_name=\"BAAI/bge-large-en-v1.5\"); e.embed_query(\"test\")"\n\
echo "Starting DocChat application..."\n\
python run_chatbot.py --model ${MODEL_NAME:-mistral} --check_missing ${CHECK_MISSING:-True}' > start.sh && chmod +x start.sh

CMD ["./start.sh"]