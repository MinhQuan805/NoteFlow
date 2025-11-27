import json
from config.qdrantClient import client
from embeddings.encoder import encode_text
from chunking.fixedChunk import fixed_size_chunks
from chunking.sentenceChunk import sentence_chunks
from chunking.semanticChunk import semantic_chunks
from qdrant_client import models

def ingest_data(json_path="src/data/movies.json", collection_name="movie_search"):
    # Load movie data
    with open("src/data/movies.json", "r") as f:
        movies_data = json.load(f)

    # Create collection if it does not exist
    points = []
    idx = 0
    for movie in movies_data:  # Process each movie
        # Fixed-size chunks
        for chunk in fixed_size_chunks(movie["description"]):
            points.append(models.PointStruct(
                id=idx,
                vector=encode_text(chunk),
                payload={**movie, "chunk": chunk, "chunking": "fixed"}
            ))
            idx += 1

        # Sentence-aware chunks  
        for chunk in sentence_chunks(movie["description"]):
            points.append(models.PointStruct(
                id=idx,
                vector=encode_text(chunk),
                payload={**movie, "chunk": chunk, "chunking": "sentence"}
            ))
            idx += 1

        # Semantic chunks
        for chunk in semantic_chunks(movie["description"]):
            points.append(models.PointStruct(
                id=idx,
                vector=encode_text(chunk),
                payload={**movie, "chunk": chunk, "chunking": "semantic"}
            ))
            idx += 1

    client.upload_points(collection_name='movie_search', points=points)
    print(f"Uploaded {idx} vectors across three chunking strategies")
