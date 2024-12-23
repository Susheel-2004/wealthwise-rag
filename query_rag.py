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
user: what is a mutual fund?
you said:


A mutual fund is a professionally managed investment vehicle that pools money from multiple investors to purchase a diversified portfolio of securities such as stocks, bonds, money market instruments, or other assets. Each investor in a mutual fund owns shares, which represent a portion of the fund's holdings.
Key Features of a Mutual Fund:

    Diversification:
        Mutual funds invest in a variety of assets to reduce risk. Instead of putting all your money in one stock or bond, mutual funds spread investments across multiple assets.

    Professional Management:
        Managed by fund managers or financial experts who make decisions on what securities to buy, hold, or sell, based on the fund's objectives.

    Pooling of Resources:
        Investors collectively pool their money, allowing individuals with smaller amounts to access diversified portfolios and professional management.

    Types of Mutual Funds:
        Equity Funds: Invest primarily in stocks, suitable for long-term growth.
        Debt Funds: Focus on fixed-income securities like bonds, offering stable returns with lower risk.
        Balanced or Hybrid Funds: Invest in a mix of stocks and bonds to balance risk and reward.
        Index Funds: Aim to replicate the performance of a specific index (e.g., S&P 500).
        Money Market Funds: Invest in short-term, low-risk securities for liquidity and safety.

    Net Asset Value (NAV):
        The price per share of a mutual fund, calculated daily based on the total value of the fund's assets minus its liabilities, divided by the number of outstanding shares.

    Liquidity:
        Most mutual funds offer liquidity, allowing investors to buy or sell shares at the fund's NAV on any business day.

    Fees:
        Mutual funds charge fees like expense ratios (for management and operations) and sometimes sales loads (commissions for buying or selling shares).

Advantages of Mutual Funds:

    Access to Professional Management: Ideal for investors with limited expertise or time.
    Diversification: Reduces the impact of poor performance by a single asset.
    Affordability: Investors can start with small amounts.
    Liquidity: Easy to buy and sell shares.
    Regulation: Mutual funds are typically regulated by government bodies (e.g., SEC in the U.S.), ensuring transparency and investor protection.

Disadvantages of Mutual Funds:

    Fees and Expenses: Management fees and other costs can eat into returns.
    No Control Over Portfolio: Investors rely on fund managers to make decisions.
    Market Risk: Returns are not guaranteed and depend on market performance.
    Tax Inefficiency: Investors may incur tax liabilities when fund managers buy or sell securities.

Example:

If 1,000 people each invest $1,000 in a mutual fund, the fund pools $1 million. The fund manager then uses this money to buy a diversified set of securities. If the securities perform well, the fund's value increases, and investors benefit in proportion to their share.

{context}
---
Answer based on the context available and also use your own knowledge to answer the question professionally and learner-friendly. And most importantly, all answers must be in the context of Indian financial market.

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
    # response = get_from_gemini(prompt)
    response = get_from_llama(prompt)

    # print("Response ready.")

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"{response}\n"

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
    response = get_from_gemini(prompt)
    #response = get_from_llama(prompt)

    return response

def get_from_gemini(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

def get_from_llama(prompt):
    model = OllamaLLM(model=MODEL)
    response = model.invoke(prompt)
    return response




# def main():
#     print(query_rag("top 20 common investment mistakes"))

# if __name__ == "__main__":
#     main()

