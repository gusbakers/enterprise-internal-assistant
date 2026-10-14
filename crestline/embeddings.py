import os
import threading
from functools import lru_cache

from fastembed import TextEmbedding

from crestline.config import MODEL_NAME

_lock = threading.Lock()


@lru_cache(maxsize=1)
def encoder():
    return TextEmbedding(model_name=MODEL_NAME, cache_dir=os.getenv("FASTEMBED_CACHE_PATH", "/tmp/crestline-models"), threads=2)


def embed(texts):
    with _lock:
        return [vector.tolist() for vector in encoder().embed(texts, batch_size=16)]


def vector_literal(vector):
    return "[" + ",".join(str(float(value)) for value in vector) + "]"
