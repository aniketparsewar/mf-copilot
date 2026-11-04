"""Rebuild exercises — W6 Days 1-2 core components, written by you.

Consolidation tested the concepts; this set rebuilds the actual
mechanisms of src/copilot.py from spec, so the seams between
components (where the quiz misses lived) become yours. Offline:
no API key needed — generation is represented by fixtures.

Run from the project root:  python exercises/rebuild_w6.py
Done when every exercise prints PASS. Do not edit the checks.
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
    except Exception as e:
        RESULTS[name] = f"FAIL ({type(e).__name__})"
    print(f"{name}: {RESULTS[name]}")


# ---------------------------------------------------------------- R1
def format_passages(results: list[dict]) -> str:
    """R1 — The citation interface (W6 Day 1's bug, rebuilt).

    The Day 1 scaffold headed each passage "[1] file :: section" and
    the model cited the NUMBER. The fix made the header BE the
    citation. TODO: join the passages with a blank line between
    them, each formatted as:

        [file :: section]
        <text>

    No numbering anywhere — every bracketed string in the output
    must be a complete, copyable citation.
    """
    return "\n\n".join(
    f"[{r['file']} :: {r['section']}]\n{r['text']}" for r in results)

    #raise NotImplementedError


def r1():
    results = [
        {"file": "incidents/INC-2025-014.md", "section": "Root Cause",
         "text": "Three transactions contained spaces in TXN-AMOUNT."},
        {"file": "copybooks/ACCTREC.cpy", "section": "ACCOUNT-RECORD",
         "text": "05 ACCT-BALANCE PIC S9(9)V99 COMP-3."},
    ]
    out = format_passages(results)
    assert "[incidents/INC-2025-014.md :: Root Cause]" in out
    assert "[copybooks/ACCTREC.cpy :: ACCOUNT-RECORD]" in out
    assert "[1]" not in out and "[2]" not in out, "no passage numbers"


# ---------------------------------------------------------------- R2
def parse_citations(text: str, results: list[dict]) -> tuple[list, list]:
    """R2 — The citation checker (tag rule), rebuilt.

    TODO: find every [...] citation in `text`; a citation is VALID
    only if its exact "file :: section" string matches a retrieved
    result's (file, section) pair. Return (valid, invalid) in order
    of appearance. Hallucinated provenance is surfaced, not dropped.
    """
    import re
    cited = re.findall(r"\[([^\[\]]+)\]", text)
    #print("CITED:", cited)   
    retrieved = {f"{r['file']} :: {r['section']}" for r in results}  # step 2
    valid, invalid = [], []
    # step 3: loop over `cited` — NOT over results.
    #   each cited string: in retrieved -> valid, else -> invalid.
    #   append the bare string (no brackets).
    for cite in cited:
        if cite in retrieved:
            valid.append(cite)
        else:
            invalid.append(cite)
    return valid, invalid
    #raise NotImplementedError


def r2():
    retrieved = [
        {"file": "incidents/INC-2025-021.md", "section": "(title)"},
        {"file": "copybooks/ACCTREC.cpy", "section": "ACCOUNT-RECORD"},
        {"file": "incidents/INC-2025-021.md", "section": "Root Cause"},
    ]
    # The real Day 1 failure: passage number cited as if it were a file.
    v, i = parse_citations("It caused INC-2025-021. [1 :: Summary]", retrieved)
    assert v == [] and i == ["1 :: Summary"], (v, i)
    # The post-fix form: verbatim header, valid.
    v, i = parse_citations(
        "The record grew. [copybooks/ACCTREC.cpy :: ACCOUNT-RECORD]",
        retrieved)
    assert v == ["copybooks/ACCTREC.cpy :: ACCOUNT-RECORD"] and i == []
    # Right file, section never retrieved: still invalid under tag rule.
    v, i = parse_citations(
        "Status 39 on open. [incidents/INC-2025-021.md :: Summary]",
        retrieved)
    assert v == [] and i == ["incidents/INC-2025-021.md :: Summary"]


# ---------------------------------------------------------------- R3
def error_profile(probes: list[tuple[str, float]], gate: float) -> tuple[int, int]:
    """R3 — A threshold's error profile (W6 Day 2, as code).

    probes: (kind, top_cos); kind "in" must answer, "out" must be
    refused. A probe is gate-refused when top_cos < gate.
    TODO: return (false_accepts, false_refusals) — out-probes the
    gate waves through, and in-probes the gate refuses.
    """
    false_accepts = 0
    false_refusals = 0
    for probe in probes:
        if probe[0] == "out" and probe[1] >= gate:
            false_accepts += 1
        elif probe[0] == "in" and probe[1] < gate:
            false_refusals += 1
    return false_accepts, false_refusals
    #raise NotImplementedError


def r3():
    full = [("in", 0.458), ("in", 0.498), ("in", 0.530), ("in", 0.530),
            ("in", 0.535), ("in", 0.566), ("in", 0.571), ("in", 0.571),
            ("in", 0.592), ("in", 0.617), ("in", 0.634), ("in", 0.646),
            ("in", 0.341), ("in", 0.579),
            ("out", 0.160), ("out", 0.312), ("out", 0.341),
            ("out", 0.406), ("out", 0.469)]
    eval_only = [p for p in full if p not in
                 [("in", 0.341), ("in", 0.579), ("out", 0.312), ("out", 0.469)]]
    assert error_profile(full, 0.25) == (4, 0), "placeholder leaks 4 of 5"
    assert error_profile(full, 0.44) == (1, 1), \
        "COND waves through; the layout paraphrase is falsely refused"
    assert error_profile(eval_only, 0.44) == (0, 0), \
        "on the eval contract alone, 0.44 is perfect — probes tell more"


# ---------------------------------------------------------------- R4
def decide_action(subject_in_passages: bool,
                  premise_contradicted: bool) -> str:
    """R4 — The rule 3 <-> rule 4 precedence, as an executable policy.

    Day 2's two false-premise failures were this decision made by
    vibes: June needed correction but got compliance; TXN-AMOUNT
    needed correction but got refusal. TODO: encode the precedence
    and return "answer", "correct", or "refuse":
    - subject absent from the passages -> refuse (nothing to stand on)
    - subject present, premise contradicted -> correct the premise
    - subject present, premise fine -> answer
    This function is the spec for Day 3's prompt fix.
    """
    if not subject_in_passages:
        return "refuse"
    elif premise_contradicted:
        return "correct"
    else:
        return "answer"
    raise NotImplementedError


def r4():
    assert decide_action(False, False) == "refuse"   # CEO salary
    assert decide_action(False, True) == "refuse"    # nothing to correct FROM
    assert decide_action(True, True) == "correct"    # June; TXN-AMOUNT
    assert decide_action(True, False) == "answer"    # status 39


# ---------------------------------------------------------------- R5
def fact_windows(doc, needle: str) -> list[tuple[str, int, int]]:
    """R5 — The provenance puzzle (why the March citation 'failed').

    TODO: using chunk_fixed, return (section_tag, start, end) for
    every fixed window of `doc` whose text contains `needle`.
    """
    from src.chunking import chunk_fixed
    out = []
    for chunk in chunk_fixed(doc):
        if needle in doc.text[chunk.start:chunk.end]:
            out.append((chunk.section, chunk.start, chunk.end))
    return out
    
def r5():
    from src.chunking import chunk_fixed  
    from src.corpus import load_corpus
    doc = {d.file: d for d in load_corpus()}["incidents/INC-2025-014.md"]
    hits = fact_windows(doc, "spaces in TXN-AMOUNT")
    # The March fact sentence (char 335) is contained in exactly ONE
    # window — and that window is tagged (title), not Root Cause.
    # That is the whole tag-vs-span story in a single assert.
    assert hits == [("(title)", 0, 500)], hits


if __name__ == "__main__":
    for name, fn in [("R1 format_passages", r1), ("R2 parse_citations", r2),
                     ("R3 error_profile", r3), ("R4 decide_action", r4),
                     ("R5 fact_windows", r5)]:
        check(name, fn)
    done = sum(1 for v in RESULTS.values() if v == "PASS")
    print(f"\n{done}/5 exercises passing")
