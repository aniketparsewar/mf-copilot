"""Consolidation exercises — W5 + W6 keeper concepts, as code you write.

New course rule (2026-11-02): understanding is demonstrated, not
assumed. Each exercise is a mechanism you have USED but not yet
reliably NAMED on a quiz. Implement the TODOs; the checks use real
cases from your own W5/W6 runs. Do not edit the checks.

Run from the project root:  python exercises/consolidation.py
Done when every exercise prints PASS.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

RESULTS = {}


def check(name, fn):
    try:
        fn()
        RESULTS[name] = "PASS"
    except NotImplementedError:
        RESULTS[name] = "TODO"
    except AssertionError as e:
        RESULTS[name] = f"FAIL ({e})"
    print(f"{name}: {RESULTS[name]}")


# ---------------------------------------------------------------- E1
def rrf_fuse(rankings: list[list[str]], k_const: int = 60) -> list[str]:
    """E1 — Reciprocal Rank Fusion, by hand.

    W5 keeper: hybrid fuses RANKS, not scores, because BM25 scores
    (unbounded) and cosine scores ([0,1]) are incommensurable.

    TODO: score each item as the sum over rankings of
    1 / (k_const + rank + 1), where rank is 0-based. Return the items
    ordered by score descending; break ties by first appearance.
    two faults, and the first is worse than the second. Your out list holds every occurrence, and sorted returns all of them: fixture 2 came back ['x','y','z','z','y','x'] — six items for three chunks, so even fixture 1 fails. Underneath that, the sort key is occurrence count — rank never enters the computation at all. 
    """
    scores = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking):
            scores[item] = scores.get(item, 0) + 1 / (k_const + rank + 1)
    return sorted(scores.keys(), key=lambda x: -scores[x])

def e1():
    assert rrf_fuse([["a", "b", "c"], ["b", "a", "d"]]) == ["a", "b", "c", "d"], \
        "symmetric lists: consistency wins, ties by first appearance"
    assert rrf_fuse([["x", "y", "z"], ["z", "y", "x"]]) == ["x", "z", "y"], \
        "y is 2nd in both lists yet loses to x/z: RRF rewards top ranks"


# ---------------------------------------------------------------- E2
def diagnose(top_cos: float, gate: float, relevant_in_pool: bool,
             relevant_rank: int | None, refused: bool,
             expect_refusal: bool, answer_correct: bool) -> str:
    """E2 — The layer walk, as a function.

    W6 keeper: walk the debug output top to bottom; the FIRST layer
    whose output is wrong owns the failure. Return one of:
    "ok", "gate", "recall", "ranking", "generation".

    Rules (derive them from the cases below before coding):
    - Expected refusal and got one -> "ok", whichever layer refused.
    - Expected refusal but answered -> the model let it through:
      "generation".
    - Answerable but refused -> if the gate score was below the gate,
      the gate owns it ("gate"); otherwise the model refused despite
      good evidence ("generation").
    - Answered but wrong -> if no relevant chunk was in the pool,
      "recall"; if it sat below rank 5, "ranking"; if it was in the
      top 5 and the answer is still wrong, "generation"..
      expect refusal, refused → ok
expect refusal, answered → generation
answerable, refused → top_cos < gate ? gate : generation
answerable, answered, correct → ok
answerable, answered, wrong → not in pool ? recall : rank > 5 ? ranking : generation
    """
    if expect_refusal and refused:
        return "ok"
    elif expect_refusal and not refused:
        return "generation"
    elif not expect_refusal and refused:
        if top_cos < gate:
            return "gate"
        else:
            return "generation"
    elif not expect_refusal and not refused and answer_correct:
        return "ok"
    elif not expect_refusal and not refused and not answer_correct:
        if not relevant_in_pool:
            return "recall"
        elif relevant_rank is not None and relevant_rank > 5:
            return "ranking"
        else:
            return "generation"
    



def e2():
    G = 0.44
    # DB2 (W6): gate refused an out-of-scope question -> ok
    assert diagnose(0.341, G, False, None, True, True, False) == "ok"
    # COND (W6): passed the gate (0.4686 > 0.44), MODEL refused -> ok
    assert diagnose(0.4686, G, False, None, True, True, False) == "ok"
    # TXN-AMOUNT (W6): rank-1 evidence, gate 0.6175, refused anyway
    assert diagnose(0.6175, G, True, 1, True, False, False) == "generation"
    # June premise (W6): answered, top-5 evidence, facts framed falsely
    assert diagnose(0.5297, G, True, 2, False, False, False) == "generation"
    # March under structure (W5): relevant chunk absent from the pool
    assert diagnose(0.40, G, False, None, False, False, False) == "recall"
    # Batch start under structure (W5): in pool at rank 7, below cutoff
    assert diagnose(0.40, G, True, 7, False, False, False) == "ranking"
    # Paraphrase at gate 0.44 (W6): answerable, refused by the gate
    assert diagnose(0.341, G, True, 3, True, False, False) == "gate"


# ---------------------------------------------------------------- E3
def valid_by_tag(cite_file: str, cite_section: str, retrieved) -> bool:
    """E3a — Citation validity by TAG equality: the cited (file,
    section) must be one of the retrieved chunks' tags.
    TODO: implement."""
    for chunk in retrieved:
        if chunk.file == cite_file and chunk.section == cite_section:
            return True
    return False


def valid_by_span(cite_file: str, cite_section: str, retrieved,
                  docs_by_file) -> bool:
    """E3b — Citation validity by SPAN overlap: find the cited
    section's span in that file's document (docs_by_file[cite_file]);
    valid if any retrieved chunk FROM THE SAME FILE overlaps it.
    (W5's metrics judged relevance this way; the citation checker
    should judge provenance the same way.)
    TODO: implement."""
    doc = docs_by_file.get(cite_file)
    if doc is None:
        return False
    section = next((s for s in doc.sections if s.name == cite_section), None)
    if section is None:
        return False
    for chunk in retrieved:
        if chunk.file == cite_file and chunk.start < section.end and section.start < chunk.end:
            return True
    return False



def e3():
    from src.chunking import chunk_fixed
    from src.corpus import load_corpus
    docs = {d.file: d for d in load_corpus()}
    doc = docs["incidents/INC-2025-014.md"]
    # The real retrieved set from the W6 Day 2 March run:
    retrieved = [c for c in chunk_fixed(doc) if c.start in (0, 900)]
    f, s = "incidents/INC-2025-014.md", "Root Cause"
    assert valid_by_tag(f, s, retrieved) is False, \
        "no retrieved chunk is TAGGED Root Cause"
    assert valid_by_span(f, s, retrieved, docs) is True, \
        "the (title) window 0-500 overlaps Root Cause's span 251-572"
    # Negative controls: an unretrieved section of the same file, and
    # a section of a file that was never retrieved at all.
    assert valid_by_tag(f, "Resolution", retrieved) is False
    assert valid_by_span(f, "Resolution", retrieved, docs) is False
    assert valid_by_tag("runbooks/RB-ABEND-S0C7.md", "Cause", retrieved) is False
    assert valid_by_span("runbooks/RB-ABEND-S0C7.md", "Cause", retrieved, docs) is False


# ---------------------------------------------------------------- E4
def mrr(first_ranks: list) -> float:
    """E4 — Mean Reciprocal Rank, by hand.

    W5 keeper: hit rate is rank-blind; MRR is the metric that saw
    the wrong-section problem coming. Each entry is the rank of the
    first relevant result for one question, or None for a miss.
    TODO: implement (reciprocal of rank; a miss contributes 0;
    return the mean, rounded to 3 decimals).
    right arithmetic, missed contract. 0.90666… ≠ 0.907. The docstring says round to 3 decimals; fixture 2's rank-3 terms (1/3, repeating) exist precisely to catch the omission.
    """
    sum = 0   
    for rank in first_ranks:
        if rank is not None:
            sum += 1 / rank
    return round(sum / len(first_ranks), 3)

    

def e4():
    assert mrr([1, 2, 1, None]) == 0.625
    # Reconstructs the real W5 fixed+hybrid MRR: 21 questions answered
    # at rank 1, two at rank 2, two at rank 3, none missed.
    assert mrr([1] * 21 + [2] * 2 + [3] * 2) == 0.907


# ---------------------------------------------------------------- E5
def pick_gate(probes: list[tuple[str, float]]) -> float:
    """E5 — Calibrate the refusal gate from measured scores.

    W6 keeper: a threshold is chosen from data, with a stated error
    policy — never tuned by feel. `probes` is a list of
    (kind, top_cos) where kind is "in" (must answer) or "out" (must
    refuse). Policy (fail closed, your Day 2 decision): the gate
    must refuse EVERY "out" probe, and sit in the upper half of the
    feasible window — closer to the weakest "in" than to the
    strongest "out".
    TODO: return a threshold satisfying the policy.
    anchored to the wrong numbers. max(in) and the out-spread are irrelevant. The feasible window is defined by exactly two measurements: strongest out 0.406 (gate must exceed it) and weakest in 0.458 (gate must stay under it). Your formula returned 0.523 — outside the window entirely; it would refuse real questions. Fail-closed = the upper half of that window: anything in [0.432, 0.458).
    """
    max_out = max(probe[1] for probe in probes if probe[0] == "out")
    min_in = min(probe[1] for probe in probes if probe[0] == "in")
    return (max_out + min_in) / 2

    

def e5():
    probes = [  # your real Day 2 measurements (eval cases only)
        ("out", 0.160), ("out", 0.341), ("out", 0.406),
        ("in", 0.458), ("in", 0.498), ("in", 0.530), ("in", 0.535),
        ("in", 0.566), ("in", 0.571), ("in", 0.579), ("in", 0.592),
        ("in", 0.617), ("in", 0.634), ("in", 0.646),
    ]
    g = pick_gate(probes)
    assert g > 0.406, "must refuse every out-of-scope probe"
    assert g < 0.458, "must not refuse the weakest in-corpus question"
    assert g >= (0.406 + 0.458) / 2, "fail closed: upper half of the window"


if __name__ == "__main__":
    for name, fn in [("E1 rrf_fuse", e1), ("E2 diagnose", e2),
                     ("E3 citation validity", e3), ("E4 mrr", e4),
                     ("E5 pick_gate", e5)]:
        check(name, fn)
    done = sum(1 for v in RESULTS.values() if v == "PASS")
    print(f"\n{done}/5 exercises passing")
