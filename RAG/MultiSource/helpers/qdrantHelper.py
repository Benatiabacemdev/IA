from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
import os

class QdrantHelper:
    def __init__(self):
        self.location = os.getenv("DB_QD_LOCATION")
        self.port = os.getenv("DB_QD_PORT")
        self.api_key = os.getenv("DB_QD_API_KEY")
        self.collection_name = os.getenv("DB_QD_COLLECTION_NAME")
        self.client = self.connect()

    def connect(self):        
        client = QdrantClient(self.location, port=self.port, https=False, api_key=self.api_key)
        if(not client.collection_exists(self.collection_name)):
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
            )
        return client

    def get_vectorstore(self, llmName):
        embeddings = OllamaEmbeddings(model=llmName)
        vectorstore = QdrantVectorStore(client=self.client, collection_name=self.collection_name, embedding=embeddings)
        return vectorstore
    
    def add_ToVectorStore(self, texts, vectorstore):
        return vectorstore.add_texts(texts=texts)
    
    def delete_points(self, uids):
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=uids
            )
            return True
        except Exception as e:
            print(f"Error deleting points {uids}: {e}")
            return False

