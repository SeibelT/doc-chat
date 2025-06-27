import gradio as gr
from Backend.rag.ollama_rag_class import Ollama_RAG





if __name__ == "__main__":
    import gradio as gr
    # Example usage with ChatInterface and custom example buttons
    def echo(message, history):
        print(message,"\n", history)
        print(type(message), type(history))
        #history = history or []
        #history.append([message, message])
        return [message,""]

    def click_echo(new_message, history):
        history = history or []
        history.append([new_message, new_message])  # Echo user message as bot response
        return history

    # Create the ChatInterface
    demo = gr.ChatInterface(
        fn=echo,
        multimodal=False,
        title="Echo Bot",
         
    )

    # Add custom example buttons below the ChatInterface
    with demo:
        with gr.Column():
            for example in ["hello", "hola", "merhaba"]:
                gr.Button(example).click(
                    fn= click_echo ,
                    inputs=[gr.State(example), demo.chatbot],
                    outputs=demo.chatbot
                )


    demo.launch()


if False:
    user_proficiency = "average"  # Change this to "special_needs", "average", or "basic_medical"
    model_name = "mistral"  # Change this to the desired model name
    rag = Ollama_RAG(user_proficiency, model_name)
    #rag.interactive_chat()
    def echo(message,history):
        return message
        return rag.single_question(message)

    demo = gr.ChatInterface(
        fn=echo,
        examples=["hello", "hola", "merhaba"],
        title="Echo Bot",
        show_examples=True  # Ensures example buttons are shown
    )
    demo.launch()

    #message = ("how long do i have to fast before the procedure? ") 
    #print(rag.single_question(message)) 
