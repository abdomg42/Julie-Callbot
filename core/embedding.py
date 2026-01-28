# Optional embedder for local tests.
# In your real pipeline, you already receive vector_embedding (768-dim) from upstream.

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from .static import DEFAULT_EMBED_MODEL

class Embedder:
    def __init__(self, model_name: str = DEFAULT_EMBED_MODEL):
        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    def embed_768(self, text: str) -> List[float]:
        vec = self._model.encode([text], convert_to_numpy=True, normalize_embeddings=True)[0].astype("float32")
        return vec.tolist()
