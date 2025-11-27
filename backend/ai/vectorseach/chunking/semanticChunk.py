from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def semantic_chunks(text):
    """Semantic chunking: uses embedding similarity to find natural breaks.
    Note: still constrained by the embed model's context window (same as retrievers)."""
    from llama_index.core import Document
    
    semantic_splitter = SemanticSplitterNodeParser(
        buffer_size=1,
        breakpoint_percentile_threshold=95,
        embed_model=HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    )
    nodes = semantic_splitter.get_nodes_from_documents([Document(text=text)])
    return [node.text for node in nodes]