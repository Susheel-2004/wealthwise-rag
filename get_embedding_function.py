from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain.text_splitter import TokenTextSplitter
from langchain.schema.document import Document


def get_embedding_function():
    # embeddings = BedrockEmbeddings(
    #     credentials_profile_name="default", region_name="us-east-1"
    # )
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings