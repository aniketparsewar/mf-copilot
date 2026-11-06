"""W6 Day 4: the copilot as a service (the P6 pattern, second time).

Wrapping rules inherited from earlier projects:
- The expensive object (the index) is built ONCE and shared; a
  per-request rebuild would re-embed the corpus on every call.
- The service projects the copilot's output: answer() also returns
  the retrieved chunks (full texts). Those are internal diagnostics,
  not API surface — heavy, and they leak the corpus verbatim.
- Auth fails CLOSED: if the server has no key configured, /ask is
  broken on purpose (500), never silently open.
- /health stays unauthenticated: deploy platforms health-check it,
  and it reveals nothing but a document count.

Run locally:  uvicorn app:app --port 8000
Env:          OPENAI_API_KEY, COPILOT_API_KEY (your service key)
"""
import os
import secrets

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

load_dotenv()

from src.chunking import chunk_corpus
from src.copilot import CHUNKING, answer as copilot_answer
from src.corpus import load_corpus
from src.index import Index

MAX_QUESTION_CHARS = 500  # P6's guardrail: unbounded input is a cost bug

app = FastAPI(title="Mainframe Knowledge Copilot")

_index: Index | None = None


def get_index() -> Index:
    """Lazy singleton: build the index on first use, share it after."""
    global _index
    if _index is None:
        _index = Index(chunk_corpus(load_corpus(), CHUNKING))
    return _index


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "corpus_docs": len(load_corpus())}


def require_key(x_api_key: str | None = Header(default=None)) -> None:
    """TODO(you): the API-key dependency (P6's shape, your code).

    - expected = os.environ.get("COPILOT_API_KEY"); if it is unset,
      raise HTTPException(500) — fail closed, never open.
    - if x_api_key is missing or does not match, HTTPException(401).
    - compare with secrets.compare_digest, not == (timing attacks
      are theoretical here; the habit is not).
    """
    expected = os.environ.get("COPILOT_API_KEY")
    if expected is None:
        raise HTTPException(500)
    if x_api_key is None or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(401)


@app.post("/ask")
def ask(req: AskRequest, _=Depends(require_key)) -> dict:
    """TODO(you): validate, delegate, project.

    - q = req.question.strip(); empty -> HTTPException(400);
      longer than MAX_QUESTION_CHARS -> HTTPException(413).
    - out = copilot_answer(get_index(), q) — call BOTH by these
      module-level names (the Day 4 checks stub them; that seam is
      what makes the service testable offline).
    - return ONLY: question, answer, refused, citations,
      invalid_citations, top_cos. Drop "retrieved".
    """
    q = req.question.strip()
    if not q:
        raise HTTPException(400)
    if len(q) > MAX_QUESTION_CHARS:
        raise HTTPException(413)
    out = copilot_answer(get_index(), q)
    return {"question": q, "answer": out["answer"], "refused": out["refused"], "citations": out["citations"], "invalid_citations": out["invalid_citations"], "top_cos": out["top_cos"]} 
    
