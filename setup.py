#!/usr/bin/env python3
# setup.py - Automated setup script
import subprocess
import sys
import os
import platform
import urllib.request
import time

def install_requirements():
    """Install requirements from requirements.txt"""
    if os.path.exists('requirements.txt'):
        print("📦 Installing Python dependencies...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
            print("✓ Python dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    else:
        print("❌ requirements.txt not found!")
        return False

def install_ollama():
    """Install Ollama based on the operating system"""
    system = platform.system()
    
    # Check if already installed
    try:
        subprocess.run(['ollama', '--version'], capture_output=True, check=True)
        print("✓ Ollama already installed")
        return True
    except:
        print("📥 Installing Ollama...")
    
    try:
        if system == "Darwin":  # macOS
            print("Installing Ollama for macOS...")
            subprocess.run(['brew', 'install', 'ollama'], check=True)
        elif system == "Linux":
            print("Installing Ollama for Linux...")
            subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '-o', '/tmp/install-ollama.sh'], check=True)
            subprocess.run(['sh', '/tmp/install-ollama.sh'], check=True)
        elif system == "Windows":
            print("⚠️  Windows detected. Please download and install Ollama manually from:")
            print("   https://ollama.ai/download/windows")
            print("   After installing, run this setup script again.")
            return False
        
        print("✓ Ollama installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install Ollama automatically: {e}")
        print("\nPlease install manually:")
        print("- Mac: brew install ollama")
        print("- Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        print("- Windows: Download from https://ollama.ai/download/windows")
        return False

def start_ollama_service():
    """Start Ollama service in the background"""
    try:
        # Check if already running
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Ollama service already running")
            return True
    except:
        pass
    
    print("🚀 Starting Ollama service...")
    try:
        # Start ollama serve in background
        if platform.system() == "Windows":
            subprocess.Popen(['ollama', 'serve'], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait a bit for service to start
        print("   Waiting for service to start...")
        time.sleep(5)
        
        # Verify it's running
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Ollama service started")
            return True
        else:
            print("❌ Failed to start Ollama service")
            return False
    except Exception as e:
        print(f"❌ Error starting Ollama service: {e}")
        return False

def pull_models():
    """Pull required Ollama models and download HuggingFace embeddings"""
    # Pull Ollama model
    print("\n📥 Downloading mistral (Main chat model)...")
    print("   This may take 5-10 minutes depending on your internet speed...")
    
    try:
        # Check if already exists
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'mistral' in result.stdout:
            print("✓ mistral already downloaded")
        else:
            # Pull the model
            subprocess.run(['ollama', 'pull', 'mistral'], check=True)
            print("✓ mistral downloaded successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download mistral: {e}")
        return False
    
    # Download HuggingFace embedding model
    print("\n📥 Downloading HuggingFace embedding model (BAAI/bge-large-en-v1.5)...")
    print("   This will be downloaded automatically when first used...")
    print("   The model will be cached locally for future use.")
    
    # Test if we can import and initialize the embedding model
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
        print("   Testing embedding model initialization...")
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
        # This will trigger the download if not already cached
        test_embedding = embeddings.embed_query("test")
        print("✓ HuggingFace embedding model ready")
    except Exception as e:
        print(f"⚠️  Embedding model will be downloaded on first use: {e}")
    
    return True

def check_vector_database():
    """Check if vector database exists, create if not"""
    faiss_index_path = os.path.join("Backend", "rag", "faiss_index")
    create_db_script = os.path.join("Backend", "rag", "create_vector_database_from_pdfs.py")
    
    if not os.path.exists(faiss_index_path):
        print("\n📚 Vector database not found. Creating from PDFs...")
        if os.path.exists(create_db_script):
            try:
                subprocess.run([sys.executable, create_db_script], check=True)
                print("✓ Vector database created successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Error creating vector database: {e}")
                return False
        else:
            print(f"⚠️  Cannot find {create_db_script}")
            print("   Make sure you have the complete project structure")
            return False
    else:
        print("✓ Vector database found")
        return True

def main():
    print("🏥 DocChat Automated Setup 🏥")
    print("==============================\n")
    
    # Step 1: Install Python requirements
    if not install_requirements():
        print("\n❌ Failed to install Python dependencies.")
        sys.exit(1)
    
    # Step 2: Install Ollama
    if not install_ollama():
        print("\n❌ Please install Ollama manually and run setup again.")
        sys.exit(1)
    
    # Step 3: Start Ollama service
    if not start_ollama_service():
        print("\n❌ Please start Ollama manually with: ollama serve")
        sys.exit(1)
    
    # Step 4: Pull required models
    if not pull_models():
        print("\n❌ Failed to download models. Please check your internet connection.")
        sys.exit(1)
    
    # Step 5: Check/create vector database
    check_vector_database()
    
    print("\n✅ Setup complete! Everything is ready.")
    print("\n🚀 To run DocChat:")
    print("   python app.py")
    print("\n📌 Note: Ollama service is running in the background.")
    print("   The app will open in your browser at http://localhost:7860")

if __name__ == "__main__":
    main()