"""Retrievers: vector-only, BM25-only, and hybrid (RRF fusion, as in
Project 3). Every result carries provenance — file, section, score —
because a passage you cannot cite is a passage you cannot trust.
"""
import numpy as np

from .index import Index

RRF_K = 60


def _rrf(rankings: list[list[int]], k_const: int = RRF_K) -> dict[int, float]:
    fused: dict[int, float] = {}
    for ranking in rankings:
        for rank, idx in enumerate(ranking):
            fused[idx] = fused.get(idx, 0.0) + 1.0 / (k_const + rank + 1)
    return fused


def search(index: Index, query: str, method: str, k: int = 5) -> list[dict]:
    if method == "vector":
        scores = index.vector_scores(query)
        ranking = list(np.argsort(-scores))
        smap = {i: float(scores[i]) for i in ranking}
    elif method == "bm25":
        scores = index.bm25_scores(query)
        ranking = list(np.argsort(-scores))
        smap = {i: float(scores[i]) for i in ranking}
    elif method == "hybrid":
        v_rank = list(np.argsort(-index.vector_scores(query)))
        b_rank = list(np.argsort(-index.bm25_scores(query)))
        smap = _rrf([v_rank, b_rank])
        ranking = sorted(smap, key=lambda i: -smap[i])
    else:
        raise ValueError(f"unknown method: {method}")

    out: list[dict] = []
    for idx in ranking[:k]:
        c = index.chunks[idx]
        out.append({
            "file": c.file, "section": c.section,
            "score": round(smap[idx], 4),
            "start": c.start, "end": c.end, "text": c.text,
        })
    return out
