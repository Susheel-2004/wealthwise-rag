from flask import Flask, request, render_template, jsonify, make_response
from time import sleep
from query_rag import query_rag, make_summary
# from populate_general_database import add_tuple_to_chroma
from flask_cors import CORS
from config import db
import os
import signal


app = Flask(__name__)
dbc = db.get_connection() 
CORS(app)

CHROMA_PATH = "chroma"



@app.route('/')
def home():
    return render_template('index.html')

@app.route("/query", methods=['POST'])
def user_query():
    data = request.get_json()
    query_text = data['question']
    response = query_rag(query_text)
    response_object = make_response(jsonify({"response":response}))
    response_object.status_code = 200
    return response_object


@app.route("/llm/summary", methods=["POST"])
def get_summary():
    body = request.get_json()
    print(body)
    user_id = body["user_id"]
    response = make_summary(user_id, dbc)
    response_object = make_response(jsonify({"response" : response}))
    response_object.status_code = 200
    return response_object


@app.route("/populate", methods=['POST'])
def populate():
    data = request.get_json()
    row = data['tuple']
    # add_tuple_to_chroma(row)
    response = make_response(jsonify({"response":"Populating the database"}))
    response.status_code = 200

    return response

def shutdown_server():
    pid = os.getpid()  # Get the process ID of the Flask server
    os.kill(pid, signal.SIGINT)  # Send a SIGINT signal to the process

@app.route('/shutdown', methods=['POST'])
def shutdown():
    data = request.get_json()
    if data['password'] == 'shutdown':
        response = make_response(jsonify({"response":"server shutting down"}))
        response.status_code = 200
        shutdown_server()
        return response
    response = make_response(jsonify({"response":"Incorrect password"}))
    response.status_code = 401
    return response
    
if __name__ == "__main__":
    app.run(debug=True)