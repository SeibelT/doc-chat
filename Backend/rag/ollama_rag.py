# ollama_rag.py

import os
from pathlib import Path
import time
import sys
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import StrOutputParser
from langchain.memory import ChatMessageHistory
from langchain.schema import HumanMessage, AIMessage

# Import from your existing scripts
from utils import embedding_model
from langchain_community.vectorstores import FAISS

# Directory paths - adjust as needed
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = os.path.join(ROOT_DIR, "data")
INDEX_DIR = os.path.join(ROOT_DIR, "Backend/rag/faiss_index")

# Chat history will be stored as a global variable
chat_history = ChatMessageHistory()

# Prompt template for RAG with chat history
RAG_PROMPT_TEMPLATE = """
You are a helpful assistant that answers questions about medical procedures based on the provided context.

Previous conversation:
{chat_history}

Context for the current question:
{context}

Current question: {question}

Answer the current question using the context provided and considering the previous conversation if relevant. 
If the context doesn't contain the answer, say "I don't have enough information to answer that question based on the provided context."
"""

def format_docs(docs):
    """Format documents into a string for the prompt"""
    return "\n\n".join([doc.page_content for doc in docs])

def format_chat_history(history):
    """Format chat history into a string for the prompt"""
    formatted_history = ""
    messages = history.messages
    
    for i in range(0, len(messages), 2):
        if i < len(messages):
            user_msg = messages[i].content
            formatted_history += f"Human: {user_msg}\n"
            
        if i+1 < len(messages):
            ai_msg = messages[i+1].content
            formatted_history += f"AI: {ai_msg}\n\n"
    
    return formatted_history

def print_retrieved_docs(docs, query):
    """Print the retrieved documents"""
    print("\n" + "="*50)
    print(f"QUERY: {query}")
    print("="*50)
    
    print("\nRETRIEVED DOCUMENTS:")
    print("-"*50)
    for i, doc in enumerate(docs):
        print(f"\nDocument {i+1}:")
        # Print first 200 chars of each document
        content = doc.page_content
        print(content[:200] + "..." if len(content) > 200 else content)

def print_chat_history():
    """Print the current chat history"""
    print("\n" + "="*50)
    print("CHAT HISTORY:")
    print("-"*50)
    
    messages = chat_history.messages
    for i, message in enumerate(messages):
        if isinstance(message, HumanMessage):
            print(f"Human: {message.content}")
        elif isinstance(message, AIMessage):
            print(f"AI: {message.content[:100]}..." if len(message.content) > 100 else f"AI: {message.content}")
    
    print("="*50)

def clear_chat_history():
    """Clear the chat history"""
    global chat_history
    chat_history = ChatMessageHistory()
    print("Chat history cleared.")

def interactive_chat(index_name, folder_path, model_name="mistral"):
    """Run an interactive chat session with memory-efficient resource reuse"""
    print("\n" + "="*50)
    print("INTERACTIVE RAG CHAT")
    print("Type 'exit' to quit, 'clear' to clear chat history, 'history' to view chat history")
    print("="*50)
    
    # Initialize resources ONCE outside the loop
    print("Initializing models and vector store...")
    llm = Ollama(model=model_name, temperature=0.1)
    embed_model = embedding_model()
    
    vector_store = FAISS.load_local(
        folder_path=folder_path,
        index_name=index_name, 
        embeddings=embed_model, 
        allow_dangerous_deserialization=True
    )
    
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={'score_threshold': 0.3}
    )
    
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()
    
    print("Initialization complete! Ready for chat.")
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for commands
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'clear':
            clear_chat_history()
            continue
        elif user_input.lower() == 'history':
            print_chat_history()
            continue
        
        try:
            # Add user query to chat history
            chat_history.add_user_message(user_input)
            
            # Retrieve documents using the already initialized retriever
            retrieved_docs = retriever.invoke(user_input)
            
            # Prepare inputs
            context = format_docs(retrieved_docs)
            formatted_history = format_chat_history(chat_history)
            
            chain_input = {
                "context": context, 
                "question": user_input,
                "chat_history": formatted_history
            }
            
            # Stream the response
            print("\n" + "="*50)
            print("STREAMING ANSWER:")
            print("-"*50)
            #print(context)
            #print("################ context ends ##################")


            # Initialize an empty answer to collect the streamed response
            full_answer = ""
            
            # Stream the response using the pre-initialized chain
            for chunk in chain.stream(chain_input):
                print(chunk, end="", flush=True)
                full_answer += chunk
                # Add a small delay to make the streaming visible
                time.sleep(0.01)
            
            print("\n" + "="*50)
            
            # Add AI response to chat history
            chat_history.add_ai_message(full_answer)
            #print(formatted_history)
            #print("################ format ends ##################")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Continuing to next question...")

# Example usage
if __name__ == "__main__":
    # Set up parameters
    index_name = "index"
    
    # Run interactive chat
    interactive_chat(
        index_name=index_name,
        folder_path=INDEX_DIR,
        model_name="mistral"  # You can change to other models like "llama2" if available
    )
