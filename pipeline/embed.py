import os
os.environ["TRANSFORMERS_NO_TF"] = "1"  # ← prevents TensorFlow import

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

# Load model once (small, fast, free)
MODEL_NAME = 'all-MiniLM-L6-v2'
model = SentenceTransformer(MODEL_NAME)

def embed_titles(titles: List[str]) -> np.ndarray:
    """
    Takes a list of preprocessed titles and returns their embeddings as a numpy array.
    """
    embeddings = model.encode(titles, show_progress_bar=True)
    return embeddings
