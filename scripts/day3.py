"""Day 3 exercise — the span-aware citation checker (E3, productionized).

The tag-rule checker (src/copilot.py parse_citations, rebuilt by you
as R2) commits a false accusation: when the model cites the section
whose TEXT answers the question — [INC-2025-014 :: Root Cause] — but
retrieval surfaced that content inside a differently-TAGGED window,
the tag rule brands the citation 'invalid' (hallucinated provenance)
even though the provenance is real. Your E3 valid_by_span is the fix.
This exercise wires it into the checker.

parse_citations_span(text, results, docs_by_file):
  - extract every [...] citation from text (same extraction as R2)
  - a citation is VALID if either rule accepts it:
      tag rule : its exact "file :: section" matches a retrieved result
      span rule: the cited section's span in docs_by_file[file]
                 overlaps a retrieved result FROM THE SAME FILE
  - malformed citations (no "::") are invalid
  - return (valid, invalid), bare "file :: section" strings, in
    order of appearance; hallucinated provenance is surfaced

results are production-shaped dicts: {file, section, start, end, text}.

Run from the project root:  python exercises/day3.py
Done when it prints PASS. Do not edit the checks.
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
        RESULTS[name] = f"FAIL ({type(e).__name__}: {e})"
    print(f"{name}: {RESULTS[name]}")



def parse_citations_span(text: str, results: list[dict],
                         docs_by_file: dict) -> tuple[list, list]:
    """TODO(you): implement per the module docstring. Your E3
    valid_by_span is the span rule; your R2 parse_citations is the
    extraction + tag rule. This function is those two, composed."""
    import re
    cited = re.findall(r"\[([^\[\]]+)\]", text)
    #print("CITED:", cited)   
    retrieved = {f"{r['file']} :: {r['section']}" for r in results}  # step 2
    valid, invalid = [], []

    for cite in cited:
        if cite in retrieved:
            valid.append(cite)
        elif span_accepts(cite, results, docs_by_file):   # your E3, adapted
            valid.append(cite)
        else:
            invalid.append(cite)

    return valid, invalid

    #span_accepts is your E3 valid_by_span with two adaptations: split cite on " :: " to recover file and section (no " :: " → False, which is what keeps fixture 6's [Summary] invalid without a crash), and read the result fields as dict keys — r["file"], r["start"], r["end"]
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

    

def _fixtures():
    from src.chunking import chunk_fixed
    from src.corpus import load_corpus
    docs = {d.file: d for d in load_corpus()}

    def as_results(doc, starts):
        return [{"file": c.file, "section": c.section, "start": c.start,
                 "end": c.end, "text": c.text}
                for c in chunk_fixed(doc) if c.start in starts]

    doc14 = docs["incidents/INC-2025-014.md"]
    retrieved = as_results(doc14, (0, 900))
    acct = [c for c in chunk_fixed(docs["copybooks/ACCTREC.cpy"])
            if c.section == "ACCOUNT-RECORD"][0]
    retrieved.append({"file": acct.file, "section": acct.section,
                      "start": acct.start, "end": acct.end,
                      "text": acct.text})
    return retrieved, docs


def d1():
    retrieved, docs = _fixtures()
    # 1. The March false accusation: cited section's TEXT was retrieved
    #    inside the (title) window. Tag rule says invalid; span must
    #    rescue it.
    v, i = parse_citations_span(
        "Spaces in TXN-AMOUNT caused it. "
        "[incidents/INC-2025-014.md :: Root Cause]", retrieved, docs)
    assert v == ["incidents/INC-2025-014.md :: Root Cause"] and i == [], (v, i)
    # 2. Day 1's hallucination stays invalid under both rules.
    v, i = parse_citations_span(
        "It caused INC-2025-021. [1 :: Summary]", retrieved, docs)
    assert v == [] and i == ["1 :: Summary"], (v, i)
    # 3. Verbatim retrieved header: valid by tag.
    v, i = parse_citations_span(
        "Balance is packed decimal. "
        "[copybooks/ACCTREC.cpy :: ACCOUNT-RECORD]", retrieved, docs)
    assert v == ["copybooks/ACCTREC.cpy :: ACCOUNT-RECORD"] and i == [], (v, i)
    # 4. A section of a file that was never retrieved: the span rule
    #    must not reach across files.
    v, i = parse_citations_span(
        "Status 39 on open. [incidents/INC-2025-021.md :: Summary]",
        retrieved, docs)
    assert v == [] and i == ["incidents/INC-2025-021.md :: Summary"], (v, i)
    # 5. Same file, section whose span no retrieved window overlaps:
    #    invalid under both rules.
    v, i = parse_citations_span(
        "It was resolved. [incidents/INC-2025-014.md :: Resolution]",
        retrieved, docs)
    assert v == [] and i == ["incidents/INC-2025-014.md :: Resolution"], (v, i)
    # 6. Malformed citation (no file :: section shape): invalid,
    #    never a crash.
    v, i = parse_citations_span(
        "See the notes. [Summary]", retrieved, docs)
    assert v == [] and i == ["Summary"], (v, i)


if __name__ == "__main__":
    check("D1 parse_citations_span", d1)
    done = sum(1 for v in RESULTS.values() if v == "PASS")
    print(f"\n{done}/1 exercises passing")
