# ollama_manager.py
import subprocess
import sys
import platform
import psutil  # pip install psutil

def is_ollama_running():
    """Check if Ollama is running"""
    for proc in psutil.process_iter(['pid', 'name']):
        if 'ollama' in proc.info['name'].lower():
            return True, proc.info['pid']
    return False, None

def stop_ollama():
    """Stop Ollama service"""
    running, pid = is_ollama_running()
    if running:
        print(f"Stopping Ollama (PID: {pid})...")
        if platform.system() == "Windows":
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
        else:
            subprocess.run(['kill', str(pid)], check=True)
        print("✓ Ollama stopped")
    else:
        print("Ollama is not running")

def start_ollama():
    """Start Ollama service"""
    if is_ollama_running()[0]:
        print("Ollama is already running")
        return
    
    print("Starting Ollama...")
    if platform.system() == "Windows":
        subprocess.Popen(['ollama', 'serve'], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✓ Ollama started")

def status():
    """Check Ollama status"""
    running, pid = is_ollama_running()
    if running:
        print(f"✓ Ollama is running (PID: {pid})")
        # Try to list models
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            print("\nInstalled models:")
            print(result.stdout)
        except:
            pass
    else:
        print("✗ Ollama is not running")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "start":
            start_ollama()
        elif command == "stop":
            stop_ollama()
        elif command == "status":
            status()
        else:
            print("Usage: python ollama_manager.py [start|stop|status]")
    else:
        status()