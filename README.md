# Mainframe Knowledge Copilot (W6)

A grounded Q&A copilot over a synthetic mainframe knowledge base
(COBOL copybooks, operations runbooks, incident notes) — generation
layered on top of the retrieval baseline proven in W5
(mf-search: fixed chunking + hybrid retrieval, benchmarked on 25
golden questions).

It answers only from retrieved passages, cites `[file :: section]`
for every claim, machine-checks its own citations against what was
retrieved, and refuses questions the knowledge base cannot answer.

## Run

```bash
pip install -r requirements.txt
cp .env.example .env   # add your OpenAI key
python scripts/ask.py "What does file status 39 mean?"
python scripts/ask.py --debug "Why did the batch fail in March?"
```

## What I learned

_(filled in at the end of the project)_
