"""Retrieval metrics over the golden question set: hit rate, recall@k,
and mean reciprocal rank (MRR).

A retrieved chunk counts as relevant to a question when it comes from
the right file AND its character span overlaps the relevant section's
span. Span overlap — not section-name equality — so fixed-size chunks
that straddle a section boundary are judged fairly.
"""
from .corpus import Doc


def _span(doc: Doc, key: str):
    key = key.lower()
    for s in doc.sections:
        if key in s.name.lower():
            return s
    return None


def _hits(result: dict, rel: dict, docs_by_file: dict[str, Doc]) -> bool:
    if result["file"] != rel["file"]:
        return False
    span = _span(docs_by_file[rel["file"]], rel["section"])
    return bool(span) and result["start"] < span.end and span.start < result["end"]


def evaluate(run: dict[str, list[dict]], questions: list[dict],
             docs: list[Doc], k: int = 5) -> dict:
    docs_by_file = {d.file: d for d in docs}
    hit = rec = rr = 0.0
    per_question: list[dict] = []
    for q in questions:
        results = run[q["question"]][:k]
        found = sum(
            1 for rel in q["relevant"]
            if any(_hits(r, rel, docs_by_file) for r in results)
        )
        first_rank = next(
            (i + 1 for i, r in enumerate(results)
             if any(_hits(r, rel, docs_by_file) for rel in q["relevant"])),
            None,
        )
        hit += 1.0 if found else 0.0
        rec += found / len(q["relevant"])
        rr += 1.0 / first_rank if first_rank else 0.0
        per_question.append({
            "question": q["question"], "found": found,
            "of": len(q["relevant"]), "first_rank": first_rank,
        })
    n = len(questions)
    return {
        "hit_rate": round(hit / n, 3),
        "recall": round(rec / n, 3),
        "mrr": round(rr / n, 3),
        "per_question": per_question,
    }
