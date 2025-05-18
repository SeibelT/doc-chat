from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

def prompt_template(system_prompt, input_query, retrieved_context, chat_history=None ):

    #prompt creation
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         f"{system_prompt}"),
        (
        "human", f"Here is the related documents {retrieved_context} to answer the question:"
                 "Please go through it, and also retrieved context and think carefully about the context before answering the question, "
                 f"now review the question: {input_query}  and provide an answer to this question using only the above provided context. "
                 " Answer:")
    ])


    return prompt

