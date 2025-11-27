from config.qdrantClient import client
from embeddings.encoder import encode_text

def search_and_compare(query, k=3):
    """Compare search results across all three chunking strategies"""
    print(f"Query: '{query}'\n")
    
    for strategy in ['fixed', 'sentence', 'semantic']:
        results = client.query_points(
            collection_name='movie_search',
            query=encode_text(query),
            using=strategy,
            limit=k,
        )
        
        print(f"--- {strategy.upper()} CHUNKING ---")
        for i, point in enumerate(results.points, 1):
            payload = point.payload
            print(f"{i}. {payload['name']} ({payload['year']}) | Score: {point.score:.3f}")
            print(f"   Chunk: {payload['chunk'][:100]}...")
        print()