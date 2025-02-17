# chatbot/caching.py
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict

class EmbeddingCache:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.cache: Dict[str, np.ndarray] = {}

    def get_embedding(self, text: str) -> np.ndarray:
        if text not in self.cache:
            self.cache[text] = self.model.encode(text)
        return self.cache[text]