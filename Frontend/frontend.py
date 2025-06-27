import gradio as gr
import yaml
from ..Backend.rag_model import dummy_model

class ChatApp:
    def __init__(self,Model ,frontend_dict_path = "./Frontend/assets/frontend_text.yaml"):
        with open(frontend_dict_path, "r", encoding='utf-8') as file:
            frontend_text = yaml.safe_load(file)

        self.language_modes = frontend_text["language_modes"]
        self.topics =frontend_text["topics"]
        self.topic_questions =frontend_text["topic_questions"]
        self.html_code =frontend_text["html_code"]
        self.language_mode = gr.State("standard")

        self.Model = Model

    def respond(self,message, history): 
        response = self.Model.single_question(message)
        return response



    # Navigation
    def go_to_chat(self,lang_mode):
        self.language_mode.value = self.language_modes[lang_mode]
        self.Model.set_language_prompt(self.language_mode.value)
        return "page3", lang_mode

    def go_to_start(self):
        return "page1"

    # Thema wählen und Fragen in Chat laden
    def update_topic_and_history(self,topic, lang):
        questions = self.topic_questions.get(topic, [])
        history = [(q, f"[{lang} | {topic}] Demo-Antwort auf: {q}") for q in questions]
        return topic, f"## Topic: {topic}", history



    def build(self):
        # UI
        with gr.Blocks(css=".gradio-container { max-width: 800px; margin: auto; }") as demo:
            current_page = gr.State("page1")
            selected_lang = gr.State("Standard")
            selected_topic = gr.State(self.topics[0])



            with gr.Column(visible=True) as page1:
                with gr.Row():
                    gr.Image(value="./Frontend/assets/LogoP1.png", height=250, width=250, show_label=False, show_download_button=False, elem_id="icon")
                gr.Markdown("## How should I talk to you?")
                for idx, (key,val) in enumerate(self.language_modes.items()):
                    gr.Button(val, elem_id=f"lang-button-{idx}").click(self.go_to_chat, [gr.State(key)], [current_page, selected_lang])

            with gr.Column(visible=False) as page3:
                topic_heading = gr.Markdown("##")
                gr.Markdown("### Choose a topic:")
                chat = gr.ChatInterface(
                    fn=self.respond,
                    examples=["hello", "hola", "merhaba"],
                    title="Echo Bot",
                    
                )


            def render(page, lang=None, topic=None):
                return {
                    page1: gr.update(visible=page == "page1"),
                    page3: gr.update(visible=page == "page3"),
                    topic_heading: gr.update(value=f"## Topic: {topic}" if topic else "")
                }

            current_page.change(render, [current_page, selected_lang, selected_topic], [page1, page3, topic_heading])

            gr.HTML(self.html_code)
    
        return demo




if __name__ == "__main__":
    app = ChatApp(dummy_model())
    demo = app.build()
    demo.launch()

