from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

# Initialize components
encoder = SentenceTransformer("all-MiniLM-L6-v2")

# Qdrant client for self-hosted local instance
client = QdrantClient(url="http://localhost:6333")

# Create collection with three named vectors
client.create_collection(
    collection_name='movie_search',
    vectors_config={
        'fixed': models.VectorParams(size=384, distance=models.Distance.COSINE),
        'sentence': models.VectorParams(size=384, distance=models.Distance.COSINE),
        'semantic': models.VectorParams(size=384, distance=models.Distance.COSINE),
    },
)
