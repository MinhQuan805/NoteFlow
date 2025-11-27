
from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer("all-MiniLM-L6-v2")

def encode_text(text: str):
    """
    Encode text using SentenceTransformer
    Returns a vector (list of floats)
    """
    vector = encoder.encode(text)
    return vector.tolist()
