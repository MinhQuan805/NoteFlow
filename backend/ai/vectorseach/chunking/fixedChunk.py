from transformers import AutoTokenizer
from llama_index.core.node_parser import SentenceSplitter, SemanticSplitterNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
MAX_TOKENS = 40


def fixed_size_chunks(text, size=MAX_TOKENS):
    """Fixed-size chunking: splits at exact token boundaries"""
    tokens = tokenizer.encode(text, add_special_tokens=False)
    return [
        tokenizer.decode(tokens[i:i+size], skip_special_tokens=True)
        for i in range(0, len(tokens), size)
    ]