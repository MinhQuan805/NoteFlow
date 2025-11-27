from transformers import AutoTokenizer
from llama_index.core.node_parser import SentenceSplitter

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
MAX_TOKENS = 40

def sentence_chunks(text):
    """Sentence-aware chunking: respects sentence boundaries"""
    splitter = SentenceSplitter(chunk_size=MAX_TOKENS, chunk_overlap=10)
    return splitter.split_text(text)