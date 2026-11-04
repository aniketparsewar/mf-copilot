"""Indexes over a chunk list: vector (OpenAI embeddings + numpy cosine)
and BM25 (rank_bm25). Embeddings are cached on disk by content hash —
re-running the benchmark must not re-buy the same vectors.
"""
import hashlib
import json
import re
from pathlib import Path

import numpy as np
from openai import OpenAI
from rank_bm25 import BM25Okapi

from .chunking import Chunk

CACHE_DIR = Path(".cache")
EMBED_MODEL = "text-embedding-3-small"

_client_instance = None


def _client():
    global _client_instance
    if _client_instance is None:
        _client_instance = OpenAI()  # reads OPENAI_API_KEY
    return _client_instance


def _key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def embed_texts(texts: list[str]) -> np.ndarray:
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / "embeddings.json"
    cache: dict = {}
    if cache_file.exists():
        cache = json.loads(cache_file.read_text(encoding="utf-8"))
    missing = [t for t in texts if _key(t) not in cache]
    if missing:
        resp = _client().embeddings.create(model=EMBED_MODEL, input=missing)
        for t, item in zip(missing, resp.data):
            cache[_key(t)] = item.embedding
        cache_file.write_text(json.dumps(cache), encoding="utf-8")
    return np.array([cache[_key(t)] for t in texts], dtype=np.float32)


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class Index:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        vecs = embed_texts([c.text for c in chunks])
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        self.vectors = vecs / np.maximum(norms, 1e-9)
        self.bm25 = BM25Okapi([tokenize(c.text) for c in chunks])

    def vector_scores(self, query: str) -> np.ndarray:
        q = embed_texts([query])[0]
        q = q / max(float(np.linalg.norm(q)), 1e-9)
        return self.vectors @ q

    def bm25_scores(self, query: str) -> np.ndarray:
        return np.array(self.bm25.get_scores(tokenize(query)), dtype=np.float64)
