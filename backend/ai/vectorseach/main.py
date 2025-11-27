from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter, SemanticSplitterNodeParser
from llama_index.core import Document
from transformers import AutoTokenizer
from datasets import load_dataset
import json

# Load dataset
ds = load_dataset("dbpedia_14", split="train")

# Encoder
encoder = SentenceTransformer("all-MiniLM-L6-v2")
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
MAX_TOKENS = 40

# Qdrant
client = QdrantClient(url="http://localhost:6333")
collection_name = "dbpedia_14_vectors"

hnsw_config = models.HnswConfigDiff(m=16, ef_construct=200)

if client.collection_exists(collection_name):
    client.delete_collection(collection_name)

client.create_collection(
    collection_name=collection_name,
    vectors_config={
        "fixed": models.VectorParams(size=384, distance=models.Distance.COSINE),
        "sentence": models.VectorParams(size=384, distance=models.Distance.COSINE),
        "semantic": models.VectorParams(size=384, distance=models.Distance.COSINE),
    },
    optimizers_config=models.OptimizersConfigDiff(default_segment_number=2),
)

print("Collection created successfully.")

# Chunking
def fixed_size_chunks(text):
    tokens = tokenizer.encode(text, add_special_tokens=False)
    return [
        tokenizer.decode(tokens[i:i + MAX_TOKENS])
        for i in range(0, len(tokens), MAX_TOKENS)
    ]

sentence_splitter = SentenceSplitter(chunk_size=MAX_TOKENS, chunk_overlap=10)

def sentence_chunks(text):
    return sentence_splitter.split_text(text)

semantic_splitter = SemanticSplitterNodeParser(
    buffer_size=1,
    breakpoint_percentile_threshold=95,
    embed_model=HuggingFaceEmbedding("sentence-transformers/all-MiniLM-L6-v2")
)

def semantic_chunks(text):
    nodes = semantic_splitter.get_nodes_from_documents([Document(text=text)])
    return [node.text for node in nodes]

# Ingest
def ingest_data(batch_size=1000):
    points = []
    idx = 0

    for doc in ds:
        text = doc["content"]
        title = doc["title"]
        label = doc["label"]

        payload = {
            "title": title,
            "content": text,
            "label": int(label),
        }

        # Fixed chunks
        for chunk in fixed_size_chunks(text):
            points.append(models.PointStruct(
                id=idx,
                vector={"fixed": encoder.encode(chunk).tolist()},
                payload={**payload, "chunk": chunk, "chunking": "fixed"}
            ))
            idx += 1

        # Sentence chunks
        for chunk in sentence_chunks(text):
            points.append(models.PointStruct(
                id=idx,
                vector={"sentence": encoder.encode(chunk).tolist()},
                payload={**payload, "chunk": chunk, "chunking": "sentence"}
            ))
            idx += 1

        # Semantic chunks
        for chunk in semantic_chunks(text):
            points.append(models.PointStruct(
                id=idx,
                vector={"semantic": encoder.encode(chunk).tolist()},
                payload={**payload, "chunk": chunk, "chunking": "semantic"}
            ))
            idx += 1

        if len(points) >= batch_size:
            client.upload_points(collection_name=collection_name, points=points)
            print(f"Uploaded {len(points)} vectors...")
            points = []

    if points:
        client.upload_points(collection_name=collection_name, points=points)

    print("Ingest finished. Total vectors:", idx)

# Search
def search_and_compare(query, k=3):
    print(f"\nQuery: {query}\n")

    for strategy in ["fixed", "sentence", "semantic"]:
        results = client.query_points(
            collection_name=collection_name,
            query=encoder.encode(query).tolist(),
            using=strategy,
            limit=k,
        )

        print(f"--- {strategy.upper()} ---")
        for i, p in enumerate(results.points, 1):
            print(f"{i}. {p.payload['title']} (label={p.payload['label']})  score={p.score:.3f}")
            print("   Chunk:", p.payload["chunk"][:120], "...\n")

# Main
def main():
    ingest_data()
    while True:
        query = input("Search (or exit): ")
        if query == "exit":
            break
        search_and_compare(query)

if __name__ == "__main__":
    main()
