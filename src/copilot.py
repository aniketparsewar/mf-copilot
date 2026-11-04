"""The copilot: grounded generation over the W5-proven retrieval baseline.

Design constraints inherited from W5's measurements, not from taste:
- Chunking/retriever: fixed + hybrid won the benchmark (hit 1.0, MRR
  0.907). The copilot retrieves with the measured winner.
- MRR was below 1.0 even for the winner: the right section is not
  always rank 1. So generation must CITE the section each claim comes
  from, and citations are checked against what was actually retrieved.
- Structure chunking failed by isolation; fixed's bleed supplies
  context. Either way, retrieval can return passages that do not
  answer the question — so the copilot must be able to REFUSE.

Refusal gate: hybrid's RRF scores are rank artifacts (compressed near
0.03) and cannot serve as an absolute threshold. The gate therefore
uses the top vector cosine similarity, an absolute measure. The value
below is a PLACEHOLDER: Day 2 calibrates it from measured scores of
in-corpus vs out-of-corpus questions. Do not tune it by feel.
"""
import re

import numpy as np
from openai import OpenAI

from .index import Index
from .search import search
from .corpus import load_corpus
DOCS_BY_FILE = {d.file: d for d in load_corpus()}
MODEL = "gpt-4o-mini"
CHUNKING = "fixed"          # the W5 benchmark winner
METHOD = "hybrid"           # the W5 benchmark winner
TOP_K = 5
GATE_COS = 0.44            
REFUSAL = "I don't have that in the knowledge base."

SYSTEM = """You are a mainframe operations copilot. You answer ONLY from \
the numbered passages provided. Rules:

1. Every factual claim in your answer must end with a citation in the \
form [file :: section], copying a passage's bracketed header verbatim.
2. Quote exact values verbatim: codes (S0C7, 39), times (21:00), PIC \
clauses, field names. Do not paraphrase numbers.
3. If the passages do not contain the answer, reply with exactly: \
"I don't have that in the knowledge base." — no citation, no guess.
4. If the question assumes something the passages contradict, correct \
the premise from the passages and cite the correction.
5. Never use knowledge from outside the passages. Keep answers short: \
the fact, then the citation."""

_client_instance: OpenAI | None = None


def _client() -> OpenAI:
    global _client_instance
    if _client_instance is None:
        _client_instance = OpenAI()
    return _client_instance


def _passages(results: list[dict]) -> str:
    return "\n\n".join(
        f"[{r['file']} :: {r['section']}]\n{r['text']}"
        for r in results
    )



_CITE = re.compile(r"\[([^\[\]]+?)\]")

#Replace the body of parse_citations with your composed version, but keep the two-argument signature parse_citations(text, results) — answer() and everything downstream call it that way; use the module-level DOCS_BY_FILE inside instead of a third parameter.
def parse_citations(text: str, results: list[dict]) -> tuple[list[str], list[str]]:
    """Split bracketed citations into (valid, invalid).

    A citation is valid only if it names a (file, section) pair that was
    actually retrieved for this question. An invalid citation is
    hallucinated provenance — the failure mode this project exists to
    catch — so it is surfaced, never silently dropped.
    """
    cited = re.findall(r"\[([^\[\]]+)\]", text)
    #print("CITED:", cited)   
    retrieved = {f"{r['file']} :: {r['section']}" for r in results}  # step 2
    valid, invalid = [], []
    for cite in cited:
        if cite in retrieved:
            valid.append(cite)
        elif span_accepts(cite, results, DOCS_BY_FILE):   # your E3, adapted
            valid.append(cite)
        else:
            invalid.append(cite)
    return valid, invalid

def span_accepts(cite, results, docs_by_file):
    if " :: " not in cite:
        return False                      # malformed: [Summary], fixture 6
    file, name = cite.split(" :: ")
    doc = docs_by_file.get(file)
    if doc is None:
        return False
    sec = next((s for s in doc.sections if s.name == name), None)
    if sec is None:
        return False
    for chunk in results:
        if chunk["file"] == file and chunk["start"] < sec.end \
                and sec.start < chunk["end"]:
            return True
    return False


def answer(index: Index, question: str, k: int = TOP_K) -> dict:
    results = search(index, question, METHOD, k)
    top_cos = float(np.max(index.vector_scores(question))) if results else 0.0
    if top_cos < GATE_COS:
        return {"question": question, "refused": True, "answer": REFUSAL,
                "citations": [], "invalid_citations": [],
                "retrieved": results, "top_cos": round(top_cos, 4)}
    resp = _client().chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user",
             "content": f"Passages:\n{_passages(results)}\n\nQuestion: {question}"},
        ],
    )
    text = (resp.choices[0].message.content or "").strip()
    valid, invalid = parse_citations(text, results)
    return {"question": question, "refused": text == REFUSAL,
            "answer": text, "citations": valid,
            "invalid_citations": invalid,
            "retrieved": results, "top_cos": round(top_cos, 4)}
