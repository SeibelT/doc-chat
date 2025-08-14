FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libxrender1 \
    libgl1-mesa-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create necessary directories first
RUN mkdir -p meta_data/faiss_index meta_data/output data

# Copy ONLY requirements.txt first (for better caching)
COPY requirements.txt .

# Install Python dependencies (this layer will be cached if requirements.txt doesn't change)
RUN pip install -r requirements.txt

# Copy application files AFTER installing dependencies
# This way, code changes won't invalidate the pip install cache
COPY . .

# Expose Gradio port
EXPOSE 7860

# Run the Docker-specific entrypoint
#CMD ["tail", "-f", "/dev/null"]
CMD ["python", "docker_entrypoint.py"]