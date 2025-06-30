import gradio as gr
import yaml


class ChatApp:
    def __init__(self,Model ,frontend_dict_path = "./Frontend/assets/frontend_text.yaml"):
        with open(frontend_dict_path, "r", encoding='utf-8') as file:
            frontend_text = yaml.safe_load(file)

        self.language_modes = frontend_text["language_modes"]
        self.topics = list(frontend_text["topic_questions"].keys()) 
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

    def change_examplequestions(self,topic):
        self.selected_topic = gr.State(topic)
        self.selected_questions.value = gr.State(self.topic_questions[self.selected_topic.value])
        return "page3"


    def go_to_start(self):
        return "page1"
    

    def build(self):
        # UI
        with gr.Blocks(css=".gradio-container { max-width: 800px; margin: auto; }") as demo:
            self.current_page = gr.State("page1")
            self.selected_lang = gr.State("Standard")
            self.selected_topic = gr.State(self.topics[0])
            self.selected_questions = gr.State(self.topic_questions[self.selected_topic.value])



            with gr.Column(visible=True) as page1:
                with gr.Row():
                    gr.Image(value="./Frontend/assets/LogoP1.png", height=250, width=250, show_label=False, show_download_button=False, elem_id="icon")
                gr.Markdown("## How should I talk to you?")
                for idx, (key,val) in enumerate(self.language_modes.items()):
                    gr.Button(key, elem_id=f"lang-button-{idx}").click(self.go_to_chat, [gr.State(key)], [self.current_page, self.selected_lang])

            with gr.Column(visible=False) as page3:
                
                bots = self.topic_questions
                
                # Create one ChatInterface per bot, each in a hidden container
                containers = {}
                for i, (bot_name, bot_info) in enumerate(bots.items()):
                    with gr.Column(visible=(i == 0)) as container:  # Show first one
                        gr.ChatInterface(
                            fn=self.respond,
                            title=bot_name,
                            examples=bot_info
                        )
                    containers[bot_name] = container
                
                
                    # Create a button for each bot
                bot_buttons = {}
                for bot_name in bots:
                    bot_buttons[bot_name] = gr.Button(bot_name)

                back_button = gr.Button("Back to the other topics")
                back_button.click(lambda: "page1", None, self.current_page)
                # Create callbacks dynamically
                for selected_name, btn in bot_buttons.items():
                    def make_callback(name=selected_name):
                        def toggle():
                            updates = []
                            for bot_name in bots:
                                is_visible = (bot_name == name)
                                updates.append(gr.update(visible=is_visible))
                            return updates
                        return toggle

                    btn.click(
                        make_callback(),
                        outputs=[containers[bot_name] for bot_name in bots]
                    )

            def render(page, lang=None, topic=None):
                return {
                    page1: gr.update(visible=page == "page1"),
                    page3: gr.update(visible=page == "page3"),
                    
                    #chat : gr.update(examples=self.selected_questions)
                }

            self.current_page.change(render, [self.current_page, self.selected_lang, self.selected_topic], [page1, page3, ])

            gr.HTML(self.html_code)
    
        return demo




class dummy_model:
    def __init__(self):
        self.language_level_prompt = "default"
    def single_question(self,message):
        return message + "  " + self.language_level_prompt
    def set_language_prompt(self,language):
        self.language_level_prompt = f"new language = {language}"


if __name__ == "__main__":
    app = ChatApp(dummy_model())
    demo = app.build()
    demo.launch()

