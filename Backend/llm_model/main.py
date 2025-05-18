from .model import chat_model
from .prompt_templates import prompt_template
from Backend.rag.rag_pipeline import rag_pipeline

input_query = "How long after the procedure i should not eat or drink?"


system_prompt = """You are an assistant for medical question-answering tasks and use the information provided through " \
                 "context, and chat history. Assume I know nothing about medicine and struggle " \
                 "to understand and have a short memory span. Use very simple words and short, precise sentences." \
                 " Don’t talk down to me, but be extra clear and respectful. Focus on explaining the " \
                 "absolute basics. If the answer needs more words, ask before continuing. If you don’t know something, " \
                 "say so."""
retrieved_context = rag_pipeline(input_query)

prompt = prompt_template(system_prompt=system_prompt, input_query=input_query, retrieved_context=retrieved_context)

llm = chat_model()

chain = prompt | llm

# Stream the generation token by token
print(f"Human: {input_query}")
print("Answer: ", end="", flush=True)
for chunk in chain.stream({"context": retrieved_context, "question": input_query}):
    print(chunk.content, end="", flush=True)
