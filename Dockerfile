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
RUN pip install -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p meta_data/faiss_index meta_data/output data

# Expose Gradio port
EXPOSE 7860

# Run the Docker-specific entrypoint
CMD ["python", "docker_entrypoint.py"]