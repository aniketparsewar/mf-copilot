# W6 — Mainframe Knowledge Copilot

## Why this project exists

Project 3 (DocChat) bolted generation onto retrieval that had never
been measured, and its failures were undiagnosable: was the answer
wrong because retrieval missed, or because generation drifted? W5
fixed the order — it proved retrieval first, with a benchmark, a
failure taxonomy, and a winning configuration. W6 now adds the
generation layer on top of that proven baseline. When something fails
here, you will know which layer owns it. That is the entire point.

## What it is

A question-answering copilot over the same 9-document mainframe
corpus (copybooks, runbooks, incidents). It retrieves with the W5
winner (fixed chunking + hybrid), generates an answer grounded only
in the retrieved passages, cites `[file :: section]` for every claim,
and refuses when retrieval has nothing to stand on.

## Design constraints inherited from W5 (measured, not taste)

- **Config**: fixed + hybrid, because the benchmark said so.
- **Citations are mandatory and machine-checked**: MRR was < 1.0 even
  for the winning config, so the right section is not always the top
  result — provenance is how a reader (and an eval) catches that.
  A citation that names a passage never retrieved is hallucinated
  provenance and is surfaced as a defect.
- **Refusal is a feature**: some questions have no answer in the
  corpus. The gate uses top vector cosine (an absolute measure), NOT
  the hybrid RRF score (a compressed rank artifact). Its threshold
  must be calibrated from measured scores, never tuned by feel.

## Layout

- `corpus/` — vendored from mf-search, unchanged (baseline integrity)
- `src/` — corpus/chunking/index/search/metrics vendored from W5;
  `copilot.py` is the new layer (prompt, gate, citation parsing)
- `scripts/ask.py` — ask questions (`--debug` shows gate + provenance)
- `scripts/evaluate.py` — answer eval skeleton (Day 3 build)
- `evals/qa.json` — 15 golden cases: 10 fact, 2 false-premise,
  3 out-of-scope. Facts verified against the corpus text.

## Day plan

- **Day 1 — grounded generation.** ask.py over the corpus. Answers
  carry citations; check provenance by hand on five questions,
  including one the corpus answers only across two documents.
- **Day 2 — refusal, calibrated.** Collect top-cosine scores for the
  12 in-corpus and 3 out-of-scope eval questions (plus paraphrases);
  pick the gate threshold from the measured gap; verify no in-corpus
  question falls below it. Attack the prompt: false premises,
  instruction-flavoured questions.
- **Day 3 — answer eval.** Implement the three scorers (facts /
  citation / refusal) in evaluate.py; run; take the worst failure
  class and fix it in the layer that owns it. Adversarial round: a
  poisoned corpus document carrying an instruction (kept outside
  corpus/ until test time) — the AgentOps side-door lesson, applied
  to retrieval.
- **Day 4 — ship.** FastAPI service (/ask, /health, own API key —
  the Project 6 pattern), deploy to Render, smoke test against the
  public URL, README "What I learned", closing quiz.

## Milestones (from the plan)

- Answers cite file :: section, and citations verify against what
  was retrieved.
- Refusal precision measured on out-of-scope questions; the gate
  threshold is a measured number with the data to defend it.
- An answer eval exists (facts / citation / refusal scored
  separately) and its worst failure class got a named fix.

## Threats to validity (say them before an interviewer does)

- 15 golden cases is a smoke signal, not a statistic.
- Substring fact-checks are brittle in both directions (Project 2).
- Same-author corpus and questions: real users phrase things worse.
