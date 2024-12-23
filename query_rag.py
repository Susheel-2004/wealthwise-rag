from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from models.get_embedding_function import get_embedding_function
from models.get_response import get_from_gemini, get_from_llama
from get_history import get_history



CHROMA_PATH = "chroma"


PROMPT_TEMPLATE = """
You are an Indian finance expert chatbot that provides accurate, actionable, and concise financial advice. You keep track of the last 5 user queries and your corresponding responses to maintain conversational context and provide cohesive guidance.

Instructions:

    Use the context of the last 5 questions and responses to tailor your reply.
    Abide by Indian-specific financial solutions, schemes, and guidelines.
    Maintain a professional yet approachable tone.

Input Format:

    User Query: The user's latest question.
    Context: Will be given
    History:
            A list of the last 5 interactions in the format:
        Question 1: User question 1
        Response 1: Your response to question 1
        Question 2: User question 2
        Response 2: Your response to question 2
        ... up to 5.

Response Structure:

    Summary/Answer: Provide a direct, context-aware answer to the user's query.
    Details: (Optional) Additional explanations or clarifications.
    Actionable Steps: Specific, practical steps for the user.
    Disclaimer: Include disclaimers as needed.


Context: {context} 
History: {history}

Question: {question}
"""



def query_rag(query_text: str):
    
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    history = get_history()

    results = db.similarity_search_with_score(query_text, k=5)
    

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
  
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text, history=history)

    response = get_from_gemini(prompt)
    # response = get_from_llama(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"{response}\n"


    return formatted_response
