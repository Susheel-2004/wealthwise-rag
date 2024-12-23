from config.chatDB import get_chatDB
from google.cloud import firestore

db = get_chatDB()

def get_history():

    questions_query = (
    db.collection("messages")
    .where("isSender", "==", True)
    .order_by("timestamp", direction=firestore.Query.DESCENDING)
    .limit(5)
    )
    questions = list(questions_query.stream())

    # Query Firestore to fetch the latest 5 replies (isSender: false)
    replies_query = (
        db.collection("messages")
        .where("isSender", "==", False)
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(5)
    )
    replies = list(replies_query.stream())

    # Pair questions with replies and format as strings
    n = min(len(questions), len(replies))

    output = ""
    for i, (question_doc, reply_doc) in enumerate(list(zip(questions, replies))[::-1]):
        question = question_doc.to_dict().get("message", "")
        reply = reply_doc.to_dict().get("message", "")
        output += f"question{i+1}: \"{question}\"\nreply{i+1}: \"{reply}\"\n"

    # Print the formatted output
    return output