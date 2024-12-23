from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import TokenTextSplitter
from langchain_core.documents import Document


def get_embedding_function():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    # embeddings = OllamaEmbeddings(model="granite-embedding")
    return embeddings