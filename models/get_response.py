import google.generativeai as genai
from langchain_ollama import OllamaLLM
import dotenv
import os


dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

MODEL = "0xroyce/plutus"
# MODEL = "llama3.1:8b"                        

def get_from_gemini(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

def get_from_llama(prompt):
    model = OllamaLLM(model=MODEL)
    response = model.invoke(prompt)
    return response