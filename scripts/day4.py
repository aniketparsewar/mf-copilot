"""Day 4 checks — the service contract, tested offline.

The checks stub app.copilot_answer and app.get_index (the seams the
scaffold requires you to use), so no OpenAI call happens: what is
being tested is YOUR service layer — auth, validation, projection —
not the model.

Run from the project root:  python exercises/day4.py
Done when every check prints PASS. Do not edit the checks.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["COPILOT_API_KEY"] = "test-key"

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


def _client():
    from fastapi.testclient import TestClient

    import app as app_module

    canned = {
        "question": "stub", "answer": "Stubbed answer. [x :: Y]",
        "refused": False, "citations": ["x :: Y"],
        "invalid_citations": [], "top_cos": 0.5,
        "retrieved": [{"file": "secret", "text": "FULL CHUNK TEXT"}],
    }
    app_module.copilot_answer = lambda index, q: canned
    app_module.get_index = lambda: None
    return TestClient(app_module.app, raise_server_exceptions=False), canned


def d1():
    c, _ = _client()
    r = c.get("/health")
    assert r.status_code == 200, r.status_code
    body = r.json()
    assert body["status"] == "ok" and body["corpus_docs"] == 9, body


def d2():
    c, _ = _client()
    r = c.post("/ask", json={"question": "What is status 39?"})
    assert r.status_code == 401, f"no key: {r.status_code}"
    r = c.post("/ask", json={"question": "What is status 39?"},
               headers={"X-API-Key": "wrong"})
    assert r.status_code == 401, f"wrong key: {r.status_code}"


def d3():
    c, canned = _client()
    r = c.post("/ask", json={"question": "What is status 39?"},
               headers={"X-API-Key": "test-key"})
    assert r.status_code == 200, r.status_code
    body = r.json()
    assert body["answer"] == canned["answer"], body
    assert body["refused"] is False and body["top_cos"] == 0.5, body
    assert "retrieved" not in body, "projection must drop retrieved chunks"


def d4():
    c, _ = _client()
    h = {"X-API-Key": "test-key"}
    r = c.post("/ask", json={"question": "   "}, headers=h)
    assert r.status_code == 400, f"empty: {r.status_code}"
    r = c.post("/ask", json={"question": "x" * 501}, headers=h)
    assert r.status_code == 413, f"over-length: {r.status_code}"


if __name__ == "__main__":
    for name, fn in [("D1 health", d1), ("D2 auth rejects", d2),
                     ("D3 ask + projection", d3), ("D4 validation", d4)]:
        check(name, fn)
    done = sum(1 for v in RESULTS.values() if v == "PASS")
    print(f"\n{done}/4 checks passing")
