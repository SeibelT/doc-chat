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
from langchain.embeddings import HuggingFaceEmbeddings
# Import from your existing scripts
#from utils import embedding_model
from langchain_community.vectorstores import FAISS


def embedding_model(model_name="BAAI/bge-large-en-v1.5"):

    return HuggingFaceEmbeddings(model_name=model_name)



class dummy_model:
    def __init__(self):
        self.language_level_prompt = "default"
    def single_question(self,message):
        return message + "  " + self.language_level_prompt
    def set_language_prompt(self,language):
        self.language_level_prompt = f"new language = {language}"


class Ollama_RAG:
    """Class for RAG with Ollama and FAISS"""
    
    def __init__(self,language_level,prompt_dict,rag_dir,model_name,logger):
        self.index_name = "index"
        

        self.language_level_prompt= self.set_language_prompt(language_level)
        # Chat history will be stored as a global variable
        self.chat_history = ChatMessageHistory()

        # Single template with system_message as a variable
        self.RAG_PROMPT_TEMPLATE = """
        {language_level_prompt}

        Previous conversation:
        {chat_history}

        Context for the current question:
        {context}

        Current question: {question}

        Answer the current question using the context provided and considering the previous conversation if relevant. 
        If the context doesn't contain the answer, say 'I do not have enough information to answer that question based on the provided context.'
        """

    
        self.logger = logger 
        self.logger.info("\n" + "="*50)
        self.logger.info("INTERACTIVE MEDICAL RAG CHAT")
        self.logger.info("Type 'exit' to quit, 'clear' to clear chat history, 'history' to view chat history")
        self.logger.info("="*50)
        self.logger.info("Prompt template:")
        self.logger.info(self.RAG_PROMPT_TEMPLATE)
        self.logger.info("="*50)

        # Initialize resources ONCE outside the loop
        self.logger.info("Initializing models and vector store...")
        self.llm = Ollama(model=model_name, temperature=0.1,)
        embed_model = embedding_model()
        
        vector_store = FAISS.load_local(
            folder_path=rag_dir,
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
        
        self.logger.info("Initialization complete! Ready for chat.")
    def set_language_prompt(self,language_level):
        return self.prompt_dict[language_level]

    def single_question(self,user_input):
        
        # Retrieve documents using the already initialized retriever
        retrieved_docs = self.retriever.invoke(user_input)
        
        # Prepare inputs
        context = self.format_docs(retrieved_docs)
        formatted_history = self.format_chat_history(self.chat_history)
        
        # Get the appropriate system message based on user proficiency
        system_message = self.language_level_prompt
        
        # Create chain with the prompt template and injected system message
        chain = self.prompt | self.llm | StrOutputParser()
        
        chain_input = {
            "system_message": system_message,
            "context": context, 
            "question": user_input,
            "chat_history": formatted_history,
            "language_level_prompt": self.language_level_prompt,
        }

        full_answer = ""
        
        # Stream the response
        for chunk in chain.stream(chain_input):       
            full_answer += chunk

        

        # Add user query and AI response to History 
        self.chat_history.add_user_message(user_input)
        self.chat_history.add_ai_message(full_answer)
        #if self.store_all: 
        #    ...
        return full_answer
        
    


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

    
