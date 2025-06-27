# Dockerfile
FROM python:3.13.5-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*


# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

WORKDIR /app

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p Backend/rag/faiss_index data logs

# Expose ports
EXPOSE 7860 11434

# Create startup script
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 5\n\
ollama pull mistral\n\
python setup.py\n\
python app.py' > start.sh && chmod +x start.sh

CMD ["./start.sh"]

