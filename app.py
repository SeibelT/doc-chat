import gradio as gr	
from Backend.rag.ollama_rag_class import Ollama_RAG

user_proficiency = "average"  # Change this to "special_needs", "average", or "basic_medical"
model_name = "mistral"  # Change this to the desired model name
rag = Ollama_RAG(user_proficiency, model_name)
#rag.interactive_chat()
def echo(message, history):
    return rag.single_question(message)

# Topics
topics = [
    "Information on the Procedure 📄🧠 ",
    "Risks & Complications 🩺🏥  ",
    "Concerns & Questions 🧍‍♂️💭",
    "Checklist & Preperation 🧾✅ ",
    "Agenda of the Day 🗓️🕒 ",
    "Aftercare ❤️‍🩹"]
# Vordefinierte Fragen pro Thema
predefined_questions = {
    "Information on the Procedure 📄🧠 ": [
        "What is an esophago-gastro-duodenoscopy and why is it being recommended?",
        "How does the doctor perform the endoscopy and how long does it take?",
        "Will I be under sedation or anesthesia, and how long does the procedure usually take?"
    ],
    "Risks & Complications 🩺🏥  ": [
        "What are the general risks associated with an endoscopy?",
        "How likely is it that I experience complications from sedation or tissue sampling?",
        "What should I do if I experience pain, bleeding, or unusual symptoms afterwards?"
    ],
    "Concerns & Questions 🧍‍♂️💭": [
        "I’m anxious about the procedure",
        "Will I be fully asleep, or can I still feel or remember parts of the exam?",
        "What happens if I react badly to the sedative or have trouble waking up?",
        "What if I have questions the day before or the morning of the procedure—who should I contact?"
    ],
    "Checklist & Preperation 🧾✅ ": [
        "What should I avoid eating or drinking before the procedure?",
        "Do I need to stop or adjust any of my medications beforehand?",
        "What documents or items do I need to bring with me on the day?"
    ],
    "Agenda of the Day 🗓️🕒 ": [
        "1. How long will I be at the clinic on the day of the procedure?",
        "What happens step-by-step from the time I arrive until I leave?",
        "Will someone need to accompany me, and can I leave right after the procedure?"
    ],
    "Aftercare ❤️‍🩹": [
       "What should I expect after the procedure—do I need to rest or take specific actions?", 
        "What signs or symptoms should make me call a doctor or seek emergency care?",
        "When can I resume normal activities like driving, working, or exercising?"
    ]
}


# Dummy Chatbot Function
def respond(message, history, topic):
    history = history or []
    response = f"[{topic}] Echo: {message}"
    history.append((message, response))
    return history, ""

with gr.Blocks() as demo:
    selected_topic = gr.State("")
    current_page = gr.State("page1")

    with gr.Row():
        gr.Markdown("##	👩‍⚕️ Doc-Chat 👨‍⚕️", elem_classes="heading")
        settings_button = gr.Button("⚙️ Accessibility Settings")

    settings_button.click(lambda: print("Settings clicked"), outputs=[])


    with gr.Column(visible=True, elem_classes="page1") as page1:
        # DocChat Bild und Begrüßung
        with gr.Blocks(css="""
            .centered-image img {
                display: inline-block;
                margin-left: auto;
                margin-right: auto;
            }
            """) as image_block:
                
                # Put the Image component inside a container with a custom clas
                 with gr.Row():
                    gr.Image(value="Backend/rag/assets/dochat1.png", label="Mein Bild", show_label=True, container=False, height=400, width=400)
        
        
        #g
        gr.Markdown("### Please choose a topic")

        for i in range(0, len(topics), 2):
            with gr.Row():
                for j in range(2):
                    if i + j < len(topics):
                        gr.Button(
                            topics[i + j],
                            elem_id=f"button-{i+j}",
                            elem_classes="colored-button"
                        ).click(
                            lambda t=topics[i + j]: (t, "page2"),
                            None,
                            [selected_topic, current_page]
                        )

    with gr.Column(visible=False, elem_classes="page2") as page2:
        topic_heading = gr.Markdown("")
        chatbot = gr.ChatInterface( fn=echo, type="messages",examples=["What is an esophago-gastro-duodenoscopy and why is it being recommended?",
        "How does the doctor perform the endoscopy and how long does it take?",
        "Will I be under sedation or anesthesia, and how long does the procedure usually take?"])
        #msg = gr.Textbox()
        #chatbot.submit(respond, [chatbot, selected_topic], [chatbot])
        back_button = gr.Button("Back to the other topics")
        back_button.click(lambda: "page1", None, current_page)

        def render_page(page, topic):
            return {
                page1: gr.update(visible=page == "page1"),
                page2: gr.update(visible=page == "page2"),
                topic_heading: gr.update(value=f"## 💬 Chat about: {topic}" if topic else "")
            }

        current_page.change(render_page, [current_page, selected_topic], [page1, page2, topic_heading])

    # Modern Dark-Blue Style with Updated Page1 and Textbox
    gr.HTML("""
        <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #E8F6EF; /* soft mint green */
            color: #2d3748;
            margin: 0;
            padding: 20px;
        }

        .page1, .page2 {
            background-color: #FDFCFB; /* gentle off-white */
            padding: 20px;
            border-radius: 14px;
            box-shadow: 0 2px 12px rgba(180, 220, 210, 0.10);
        }

        .heading h2 {
            color: #4F8A8B; /* calm teal */
        }

        .colored-button {
            width: 100%;
            height: 80px;
            font-size: 16px;
            font-weight: 600;
            color: #355C7D;
            background: white;
            border-radius: 18px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease-in-out;
            box-shadow: 0 4px 10px rgba(120,180,170,0.08);
        }

        .colored-button:hover {
            transform: scale(1.03);
            box-shadow: 0 6px 16px rgba(120,180,170,0.13);
        }

        #button-0 { background-color: #B8FFF9; }  /* pastel aqua */
        #button-1 { background-color: #FFF5BA; }  /* soft yellow */
        #button-2 { background-color: #FFD6E0; }  /* light pink */
        #button-3 { background-color: #D6F6FF; }  /* baby blue */
        #button-4 { background-color: #FFEDDA; }  /* peach */
        #button-5 { background-color: #D4F8E8; }  /* mint */
        #button-6 { background-color: #FBE7C6; }  /* light apricot */
        #button-7 { background-color: #E2F0CB; }  /* pale green */

        textarea.chat-input, input.chat-input {
            border-radius: 12px !important;
            border: 1px solid #A3C9A8;
            padding: 10px !important;
            background-color: #FDFCFB;
            color: #355C7D;
        }

        .chat-window {
            background-color: #FDFCFB;
            border-radius: 16px;
            padding: 10px;
            box-shadow: 0 4px 20px rgba(180,220,210,0.10);
            min-height: 300px;
        }

        .message.user {
            background-color: #B8FFF9;
            color: #355C7D;
            border-radius: 16px;
            padding: 10px 14px;
            margin: 8px;
            align-self: flex-end;
            max-width: 75%;
        }

        .message.bot {
            background-color: #E2F0CB;
            color: #4F8A8B;
            border-radius: 16px;
            padding: 10px 14px;
            margin: 8px;
            align-self: flex-start;
            max-width: 75%;
        }

        h2, h3 {
            color: #4F8A8B;
            font-weight: 700;
        }
        </style>
        """)

demo.launch()

# Vordefinierte Fragen pro Thema
predefined_questions = {
    "Information on the Procedure 📄🧠 ": [
        "Was passiert bei dem Eingriff?",
        "Wie funktioniert die Methode?",
        "Welche Alternativen gibt es?"
    ],
    "Risks & Complications 🩺🏥  ": [
        "Gibt es Risiken?",
        "Welche Komplikationen sind häufig?",
        "Wie wahrscheinlich sind Nebenwirkungen?"
    ],
    "Concerns & Questions 🧍‍♂️💭": [
        "Was ist, wenn ich Angst habe?",
        "Kann ich die OP verschieben?",
        "Mit wem kann ich sprechen?"
    ],
    "Checklist & Preperation 🧾✅ ": [
        "Was muss ich vor der OP tun?",
        "Darf ich vorher essen?",
        "Welche Unterlagen brauche ich?"
    ],
    "Agenda of the Day 🗓️🕒 ": [
        "Wie läuft der Tag ab?",
        "Wann bin ich dran?",
        "Wer ist mein Ansprechpartner?"
    ],
    "Aftercare ❤️‍🩹": [
        "Wie lange dauert die Erholung?",
        "Was darf ich danach nicht tun?",
        "Wann kann ich wieder arbeiten?"
    ]
}