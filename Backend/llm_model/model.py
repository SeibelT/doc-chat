
from langchain_community.chat_models import ChatOllama

def chat_model(model_name:str="mistral"):
    # Load the chat model from OllamaLLM
    print("🧠 Loading OllamaLLM Chat Model..\n")
    chat_model = ChatOllama(model=model_name,
                            streaming=True)
    print(f"✅ Ollama {model_name} model loaded successfully.\n")
    return chat_model
