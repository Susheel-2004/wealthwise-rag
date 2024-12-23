from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from get_embedding_function import get_embedding_function
import textwrap
import google.generativeai as genai
import dotenv
import os


dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


CHROMA_PATH = "chroma"

SUMMARY_TEMPLATE = """
Given the following spending data of {name}:

    Spendings(in INR): {spendings}
    Budget(in INR): {budget}

Generate a precise response with the following structure:
  Greeting :  "Hey {name} , "
    Summary of Transactions: Summarize spending across all categories.
    Deviation from Budget: Highlight deviations from preset budgets, indicating over/under-spending.
    Scope for Improvement: Suggest actionable, feasible tips for better budgeting where needed.
    Appreciation for In-Limit Purchases: Provide motivational praise for categories with spending within the limits.

Ensure the response is short, professional,user-friendly, and to the point, while still addressing all elements.
If there are no spendings at all, encourage use of our budgeting feature to track expenses and set budgets for better financial planning.
"""

NEW_PROMPT_TEMPLATE = """


{context}
---
Answer based on the context and use your own knowledge as well to answer the question.

Question: {question}

"""

MODEL = "0xroyce/plutus"
# MODEL = "llama3.1:8b"


def get_response(query, chain):
    # Getting response from chain
    response = chain({'query': query})
    
    # Wrapping the text for better output in Jupyter Notebook
    wrapped_text = textwrap.fill(response['result'], width=100)
    print(wrapped_text)

def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    # print("Chroma ready.")

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)
    # print("Search complete.")

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    # print(context_text)
    prompt_template = ChatPromptTemplate.from_template(NEW_PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print("Prompt ready.")
    

    model = OllamaLLM(model=MODEL)
    # print("Model ready.")
    response_text = model.invoke(prompt)
    # print("Response ready.")

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"{response_text}\n"

    return formatted_response


def make_summary(user_id, dbc):

    transactions_collection = dbc['transactions']       # Replace with your transactions collection
    categories_collection = dbc['categories']
    user_collection= dbc['users']

    name = user_collection.find({"user_id" : user_id}, {"username" :1, "_id":0})
    if name:
        name = name[0]["username"]
    else:
        return "User not found"

    category_names = ["Food", "Transport", "Entertainment", "Utilities"]

    # Step 1: Find category_ids for the given category_names
    category_mapping = categories_collection.find({"category_name": {"$in": category_names}})
    category_id_to_name = {category["category_id"]: category["category_name"] for category in category_mapping}

    # Step 2: Use aggregation to calculate total spendings grouped by category_id
    pipeline = [
        {"$match": {"user_id": user_id, "category_id": {"$in": list(category_id_to_name.keys())}}},
        {"$group": {"_id": "$category_id", "total_spendings": {"$sum": "$amount"}}}
    ]

    # Run the aggregation query
    aggregated_results = transactions_collection.aggregate(pipeline)

    spendings = []


    # Step 3: Map category IDs back to category names and print results
    for result in aggregated_results:
        category_name = category_id_to_name[result["_id"]]  # Map category_id back to category_name
        print(f"Category: {category_name}, Total Spendings: {result['total_spendings']}")
        spendings.append({category_name: result['total_spendings']})

    budget = """[
                {"Groceries":  250},
                {"Entertainment":100},
                {"Dining Out": 150},
                {"Transport":  100},
                {"Health & Fitness":  100}
                {"Utilities":  100}
            """
    prompt_template = ChatPromptTemplate.from_template(SUMMARY_TEMPLATE)
    prompt = prompt_template.format(name=name, spendings=spendings, budget=budget)
    model = genai.GenerativeModel("gemini-1.5-flash")
    # model = OllamaLLM(model=MODEL)
    response = model.generate_content(prompt)
    # response  = model.invoke(prompt)

    # return f"{response}\n"
    return response.text






# def main():
#     print(query_rag("top 20 common investment mistakes"))

# if __name__ == "__main__":
#     main()

