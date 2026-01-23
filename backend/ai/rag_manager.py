from ai.rag_system import RAGSystem
from typing import Dict

class RAGManager:
    """
    Manages per-notebook RAGSystem instances.
    Provides lazy initialization and caching of RAG systems.
    """
    _instances: Dict[str, RAGSystem] = {}

    @classmethod
    def get_rag(cls, notebook_id: str) -> RAGSystem:
        """
        Get or create a RAGSystem instance for the given notebook.
        """
        if notebook_id not in cls._instances:
            print(f"Initializing RAGSystem for notebook: {notebook_id}")
            cls._instances[notebook_id] = RAGSystem("ai/config.yaml", notebook_id=notebook_id)
        return cls._instances[notebook_id]

    @classmethod
    def clear_rag(cls, notebook_id: str):
        """
        Remove a cached RAGSystem instance (e.g., when notebook is deleted).
        """
        if notebook_id in cls._instances:
            del cls._instances[notebook_id]
