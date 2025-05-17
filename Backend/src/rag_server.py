import requests
import json
import sys

chat_history = []

def chat_with_ollama_stream(prompt, model="llama3"):
    url = "http://localhost:11500/api/chat"
    headers = {"Content-Type": "application/json"}

    # Prepare the full chat history + current message
    messages = chat_history + [{"role": "user", "content": prompt}]

    # Send request with streaming
    response = requests.post(
        url,
        headers=headers,
        json={
            "model": model,
            "messages": messages,
            "stream": True
        },
        stream=True  # <- important
    )

    full_response = ""

    print("Ollama: ", end="", flush=True)
    for line in response.iter_lines():
        if line:
            try:
                data = line.decode("utf-8").strip()
                if data.startswith("data: "):
                    data = data[len("data: "):]
                if data == "[DONE]":
                    break
                chunk = json.loads(data)  # ✅ Correct usage
                token = chunk.get("message", {}).get("content", "")
                print(token, end="", flush=True)
                full_response += token
            except Exception as e:
                print(f"\n[Error decoding stream chunk: {e}]\n")
                
    
    print()  # for newline after response
    # Update chat history
    chat_history.append({"role": "user", "content": prompt})
    chat_history.append({"role": "assistant", "content": full_response})

    return full_response

def main():
    print("🧠 Ollama Chat (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        try:
            reply = chat_with_ollama_stream(user_input)

            print(f"Ollama: {reply}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
