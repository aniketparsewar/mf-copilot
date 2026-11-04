# scripts/gate_scores.py
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv
load_dotenv()
import numpy as np
from src.chunking import chunk_corpus
from src.copilot import CHUNKING
from src.corpus import load_corpus
from src.index import Index

EXTRA = [
    ("paraphrase-in",  "When does the night batch kick off?"),
    ("paraphrase-in",  "What breaks when a file's layout and its definition disagree?"),
    ("near-miss-out",  "What COND codes does JOBLD01 use to skip steps?"),
    ("near-miss-out",  "What is the RACF password policy?"),
]

docs = load_corpus()
index = Index(chunk_corpus(docs, CHUNKING))
cases = json.loads(Path("evals/qa.json").read_text(encoding="utf-8"))
rows = [(c["type"], c["question"]) for c in cases] + EXTRA
for kind, q in sorted(rows, key=lambda r: float(np.max(index.vector_scores(r[1])))):
    print(f"{float(np.max(index.vector_scores(q))):.3f}  {kind:>13}  {q}")
