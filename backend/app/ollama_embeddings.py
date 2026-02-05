from typing import List
import ollama
import os
from chromadb.api.types import EmbeddingFunction, Documents


class OllamaEmbeddingFunction(EmbeddingFunction):
    """ChromaDB embedding function using Ollama"""

    def __init__(
        self,
        model_name: str = "nomic-embed-text",
        ollama_base_url: str = "http://ollama:11434"
    ):
        self.model_name = model_name
        self.client = ollama.Client(host=ollama_base_url)

    def __call__(self, input: Documents) -> List[List[float]]:
        """Generate embeddings for documents"""
        embeddings = []
        for text in input:
            response = self.client.embeddings(
                model=self.model_name,
                prompt=text
            )
            embeddings.append(response['embedding'])
        return embeddings
