from models.get_response import get_from_gemini, get_from_llama
from langchain.prompts import ChatPromptTemplate

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
Also abuse user data to provide personalized advice and recommendations.
If there are no spendings at all, encourage use of our budgeting feature to track expenses and set budgets for better financial planning.
"""

def make_summary(user_id, dbc):
    transactions_collection = dbc['transactions']       # Replace with your transactions collection
    categories_collection = dbc['categories']
    user_collection= dbc['users']
    budget_collection = dbc['userbudgets']

    name = user_collection.find({"user_id" : user_id}, {"username" :1, "_id":0})
    if name:
        name = name[0]["username"]
    else:
        return "User not found"

    category_names = ["Food", "Transport", "Entertainment", "Utilities", "Health"]

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
    # Fetch the budget document for the given user_id
    budget_doc = budget_collection.find_one({"user_id": user_id})

    # Initialize budget dictionary
    budget = {}

    if budget_doc and "budget" in budget_doc:
        # Iterate over the "budget" entries in the document
        for entry in budget_doc["budget"]:
            category_name = entry.get("category_name")
            amount = entry.get("amount")

            if category_name and amount is not None:  # Ensure valid data
                budget[category_name] = float(amount)
            else:
                print(f"Skipping invalid budget entry: {entry}")
    else:
        print("No budget document found or 'budget' field missing.")
        budget = {}
    print(budget)

    # Map category IDs back to category names and aggregate results
    spendings = []  # Initialize spendings lis


    # Step 3: Map category IDs back to category names and print results
    for result in aggregated_results:
        category_name = category_id_to_name[result["_id"]]  # Map category_id back to category_name
        print(f"Category: {category_name}, Total Spendings: {result['total_spendings']}")
        spendings.append({category_name: result['total_spendings']})

    prompt_template = ChatPromptTemplate.from_template(SUMMARY_TEMPLATE)
    prompt = prompt_template.format(name=name, spendings=spendings, budget=budget)
    response = get_from_gemini(prompt)
    #response = get_from_llama(prompt)

    return response