# history = []
# llm = ...
# if button_A:
#     instruction =  "patient is smart"
# elif button_B:
#     instruction =  "patient is special"

# history.append({"instruction":instruction})
# while chatting:
#     input = ...
#     history.append({"user":input})
#     output = llm(history)
#     history.append({"system":output})

# save_history(history)

import subprocess
import time
import requests
import os 

def start_ollama():
    with open(os.devnull, 'w') as DEVNULL:
        return subprocess.Popen(
            ["ollama", "serve"],
            stdout=DEVNULL,
            stderr=DEVNULL
        )
def wait_for_ollama_ready(timeout=30):
    print("Waiting for Ollama to be ready...")
    for _ in range(timeout):
        try:
            #$env:OLLAMA_HOST="127.0.0.1:11500"
            response = requests.get("http://localhost:11500")
            if response.status_code == 200:
                print("Ollama is ready.")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    raise TimeoutError("Ollama server did not become ready in time.")

def start_rag_server():
    print("Starting RAG server...")
    # Adjust to your RAG server command
    return subprocess.Popen(["python", "Backend\\src\\rag_server.py"])

if __name__ == "__main__":
    try:
        ollama_proc = start_ollama()
        wait_for_ollama_ready()
        rag_proc = start_rag_server()

        # Optional: Wait for both processes
        ollama_proc.wait()
        rag_proc.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        ollama_proc.terminate()
        rag_proc.terminate()