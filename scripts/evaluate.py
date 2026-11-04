"""W6 Day 3: score the copilot's ANSWERS, not just its retrieval.

Three scores per case, reported separately — an answer can be
factually right and still fail the project if its citation is wrong:
  facts     every must_contain string present (case-insensitive),
            no must_not_contain string present
  citation  at least one VALID parsed citation matches the expected
            file and section (section matched by substring)
  refusal   copilot refused exactly when the case expects refusal

Known trap, carried over from Project 2 / AgentOps: substring checks
are brittle in both directions (a correction that says "did not
corrupt" trips a naive "corrupt" ban). The must_not_contain phrases
in qa.json were chosen to thread that needle — when a score looks
wrong, read the answer before you trust the score.

Run:  python scripts/evaluate.py
Writes: results/eval_report.md
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.chunking import chunk_corpus
from src.copilot import CHUNKING, answer
from src.corpus import load_corpus
from src.index import Index

ROOT = Path(__file__).resolve().parent.parent
CASES = json.loads((ROOT / "evals" / "qa.json").read_text(encoding="utf-8"))


def score_facts(case: dict, out: dict) -> bool:
    """True when the answer carries the required facts and none of the
    banned strings. TODO(you): implement — casefold both sides."""
    """score_facts: every must_contain present in the answer, no must_not_contain present — 
    casefold both sides (the June case bans "corrupted the" while a correct answer may say "did not corrupt" — 
    read the answer before trusting a borderline score)."""
    for must_contain in case["must_contain"]:
        if must_contain.lower() not in out["answer"].lower():
            return False
    for must_not_contain in case["must_not_contain"]:
        if must_not_contain.lower() in out["answer"].lower():
            return False
    return True


def score_citation(case: dict, out: dict) -> bool | None:
    """True when a valid citation matches expected_file and contains
    expected_section_contains. None when the case expects refusal
    (no citation to judge). TODO(you): implement."""
    """score_citation: None when the case expects refusal; otherwise True iff some citation in out["citations"] 
    (the valid list) names expected_file and its section part contains expected_section_contains."""
    if case["expect_refusal"]:
        return None
    for citation in out["citations"]:
        file, _, section = citation.partition(" :: ")
        if file == case["expected_file"] and \
                case["expected_section_contains"] in section:
            return True
    return False


def score_refusal(case: dict, out: dict) -> bool:
    """True when out['refused'] == case['expect_refusal'].
    TODO(you): implement."""
    """out["refused"] == case["expect_refusal"]."""
    return out["refused"] == case["expect_refusal"]

"""fix main()'s totals in evaluate.py — 
citation rate over the 12 non-refusal cases only, 
invalid-citation headline from out["invalid_citations"], 
and write results/eval_report.md — then re-run the eval once to lock the official baseline."""

def main() -> None:
    docs = load_corpus()
    index = Index(chunk_corpus(docs, CHUNKING))
    rows = []
    for case in CASES:
        out = answer(index, case["question"])
        rows.append({
            "case": case, "out": out,
            "facts": score_facts(case, out),
            "citation": score_citation(case, out),
            "refusal": score_refusal(case, out),
        })
        print(f"{case['type']:>13}  {case['question']}")
        print(f"              {out['answer'][:160]}")
    # TODO(you): totals per score + per type, write results/eval_report.md.
    # An invalid_citations entry on ANY case is a headline finding:
    # count and report those separately, pass or fail.
    total_facts = sum(row["facts"] for row in rows)
    total_refusal = sum(row["refusal"] for row in rows)
    judged = [r for r in rows if r["citation"] is not None]
    total_citation = sum(1 for r in judged if r["citation"])
    invalid_total = sum(len(r["out"]["invalid_citations"]) for r in rows)
    invalid_cases = sum(1 for r in rows if r["out"]["invalid_citations"])
    lines = [
        "# W6 eval report",
        f"Cases: {len(rows)}",
        f"Facts: {total_facts}/{len(rows)} = {total_facts / len(rows):.3f}",
        f"Citation: {total_citation}/{len(judged)} = {total_citation / len(judged):.3f}",
        f"Refusal: {total_refusal}/{len(rows)} = {total_refusal / len(rows):.3f}",
        f"Invalid citations: {invalid_total} across {invalid_cases} case(s)",
    ]
    text = "\n".join(lines) + "\n"
    print(text)
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "eval_report.md").write_text(text, encoding="utf-8")



if __name__ == "__main__":
    main()
