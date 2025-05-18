import gradio as gr
from Backend.rag.ollama_rag_class import Ollama_RAG





if __name__ == "__main__":
    # Example usage
    user_proficiency = "average"  # Change this to "special_needs", "average", or "basic_medical"
    model_name = "mistral"  # Change this to the desired model name
    rag = Ollama_RAG(user_proficiency, model_name)
    #rag.interactive_chat()
    def echo(message):
        return rag.single_question(message)

    demo = gr.ChatInterface(fn=echo, type="messages", examples=["hello", "hola", "merhaba"], title="Echo Bot")
    demo.launch()

    #message = ("how long do i have to fast before the procedure? ") 
    #print(rag.single_question(message)) 
