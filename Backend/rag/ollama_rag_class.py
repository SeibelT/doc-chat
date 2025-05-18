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
import random

# Import from your existing scripts
from utils import embedding_model
from langchain_community.vectorstores import FAISS


class Ollama_RAG:
    """Class for RAG with Ollama and FAISS"""
    
    def __init__(self, user_proficiency,model_name="mistral"):

        # Directory paths - adjust as needed
        self.ROOT_DIR = Path(__file__).resolve().parents[2]
        self.DATA_DIR = os.path.join(self.ROOT_DIR, "data")
        self.INDEX_DIR = os.path.join(self.ROOT_DIR, "Backend/rag/faiss_index")
        self.index_name = "index"
        # Chat history will be stored as a global variable
        self.chat_history = ChatMessageHistory()

        self.question_counter = 0

        # System messages for different user proficiency levels
        self.SYSTEM_MESSAGES = {
            "special_needs": """You are an assistant for medical question-answering tasks and use the information provided through context, chat history and the procedure details. Assume I know nothing about medicine, struggle to understand and have a short memory span. Use very simple words and short, precise sentences (max. 30 words) in a simple structure. Don't talk down to me, but be extra clear and respectful. Focus on explaining the absolute basics. If the answer needs more words, ask before continuing. If you don't know something, refer to the treating physician.""",

            "average": """You are an assistant for medical question-answering tasks and use the information provided through context, chat history and the procedure details. Assume I have simple to no medical knowledge and want a simple, calm explanation. Speak casually, stay professional. Use medical terms but explain their meaning. Use clear phrases with concise information (max. 60 words). If you don't know something, refer to the treating physician.""",

            "basic_medical": """You are an assistant for medical question-answering tasks and use the information provided through context, chat history and the procedure details. Assume I understand basic anatomy and biology but am not a doctor. Use clear, professional language with casual tone. Use medical terms. Focus on the most relevant insights into the procedure. Keep answers informative (max. 90 words). If you don't have information about my question, say so."""
        }

        # Get the appropriate system message based on user proficiency
        self.user_proficiency = user_proficiency
        self.system_message = self.SYSTEM_MESSAGES[self.user_proficiency]
        
        # Single template with system_message as a variable
        self.RAG_PROMPT_TEMPLATE = """
        {system_message}

        Previous conversation:
        {chat_history}

        Context for the current question:
        {context}

        Current question: {question}

        Answer the current question using the context provided and considering the previous conversation if relevant. 
        If the context doesn't contain the answer, say "I don't have enough information to answer that question based on the provided context."
        """

        """Run an interactive chat session with memory-efficient resource reuse"""
    
    
        print("\n" + "="*50)
        print("INTERACTIVE MEDICAL RAG CHAT")
        print("Type 'exit' to quit, 'clear' to clear chat history, 'history' to view chat history")
        print("="*50)
        
        # Initialize resources ONCE outside the loop
        print("Initializing models and vector store...")
        self.llm = Ollama(model=model_name, temperature=0.1)
        embed_model = embedding_model()
        
        vector_store = FAISS.load_local(
            folder_path=self.INDEX_DIR,
            index_name=self.index_name, 
            embeddings=embed_model, 
            allow_dangerous_deserialization=True
        )
        
        self.retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={'score_threshold': 0.3}
        )
        
        # Create the prompt template once
        self.prompt = ChatPromptTemplate.from_template(self.RAG_PROMPT_TEMPLATE)
        
        print("Initialization complete! Ready for chat.")
        
    def single_question(self,user_input):
        try:
            # Add user query to chat history
            self.chat_history.add_user_message(user_input)
            
            # Retrieve documents using the already initialized retriever
            retrieved_docs = self.retriever.invoke(user_input)
            
            # Prepare inputs
            context = self.format_docs(retrieved_docs)
            formatted_history = self.format_chat_history(self.chat_history)
            
            # Get the appropriate system message based on user proficiency
            system_message = self.SYSTEM_MESSAGES[self.user_proficiency]
            
            # Create chain with the prompt template and injected system message
            chain = self.prompt | self.llm | StrOutputParser()
            
            chain_input = {
                "system_message": system_message,
                "context": context, 
                "question": user_input,
                "chat_history": formatted_history
            }

            full_answer = ""
            
            # Stream the response
            for chunk in chain.stream(chain_input):       
                full_answer += chunk

            

            
            # Add AI response to chat history
            self.chat_history.add_ai_message(full_answer)
                
            return full_answer
        except Exception as e:
                print(f"Error: {str(e)}")
                print("Continuing to next question...")
    def interactive_chat(self):
        while True:
            # Get user input
            user_input = input("\nYou: ")
            
            # Increment question counter
            self.question_counter += 1
            
            # Check for commands
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            elif user_input.lower() == 'clear':
                self.clear_chat_history()
                continue
            elif user_input.lower() == 'history':
                self.print_chat_history()
                continue
            
            try:
                # Add user query to chat history
                self.chat_history.add_user_message(user_input)
                
                # Retrieve documents using the already initialized retriever
                retrieved_docs = self.retriever.invoke(user_input)
                
                # Prepare inputs
                context = self.format_docs(retrieved_docs)
                formatted_history = self.format_chat_history(self.chat_history)
                
                # Get the appropriate system message based on user proficiency
                system_message = self.SYSTEM_MESSAGES[self.user_proficiency]
                
                # Create chain with the prompt template and injected system message
                chain = self.prompt | self.llm | StrOutputParser()
                
                chain_input = {
                    "system_message": system_message,
                    "context": context, 
                    "question": user_input,
                    "chat_history": formatted_history
                }
                
                # Stream the response
                print("\n" + "="*50)
                print(f"STREAMING ANSWER (Proficiency level: {self.user_proficiency}):")
                print("-"*50)
                
                # Initialize an empty answer to collect the streamed response
                full_answer = ""
                
                # Stream the response
                for chunk in chain.stream(chain_input):
                    print(chunk, end="", flush=True)
                    full_answer += chunk
                    # Add a small delay to make the streaming visible
                    time.sleep(0.01)
                
                print("\n" + "="*50)
                
                # Add AI response to chat history
                self.chat_history.add_ai_message(full_answer)
                
            except Exception as e:
                print(f"Error: {str(e)}")
                print("Continuing to next question...")



    def format_docs(self,docs):
        """Format documents into a string for the prompt"""
        return "\n\n".join([doc.page_content for doc in docs])

    def format_chat_history(self,history):
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

    def print_retrieved_docs(self,docs, query):
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

    def print_chat_history(self, chat_history):
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

    def clear_chat_history(self):
        """Clear the chat history"""
        self.chat_history = ChatMessageHistory()
        self.proficiency_check_done = False
        self.question_counter = 0
        print("Chat history cleared.")




if __name__ == "__main__":
    # Example usage
    user_proficiency = "average"  # Change this to "special_needs", "average", or "basic_medical"
    model_name = "mistral"  # Change this to the desired model name
    rag = Ollama_RAG(user_proficiency, model_name)
    #rag.interactive_chat()

    while True: 
        p = rag.single_question(input("You: "))
        print(p)